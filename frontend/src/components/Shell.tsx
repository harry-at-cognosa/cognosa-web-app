// The application shell (direction 9b): navigation in a floating left sidebar
// (shadcn Sidebar, collapsible to an icon strip; an off-canvas sheet on a phone),
// the page area to its right. Replaces v1.0.1's TopNavBar; which groups and items
// a user sees follows exactly the same conditions as TopNavBar did.
import { Fragment, useState, type ReactNode } from "react";
import {
  Activity,
  ArrowLeftRight,
  Brain,
  Building2,
  ChevronDown,
  ChevronsUpDown,
  Database,
  KeyRound,
  Layers,
  Library,
  ListChecks,
  ListTodo,
  Menu,
  MessagesSquare,
  PanelLeftClose,
  PanelLeftOpen,
  ScrollText,
  Search,
  SlidersHorizontal,
  UserCog,
  Users,
  type LucideIcon,
} from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarSeparator,
  useSidebar,
} from "@/components/ui/sidebar";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useNav } from "@/lib/navState";
import { useScheme, type Scheme } from "@/lib/scheme";
import { cn } from "@/lib/utils";
import { useLoggedUserStore } from "@/stores/useLoggedUserStore";
import { useNavbarStore } from "@/components/TopNavBar/useTopNavBarStore";
import SuChangeOneself from "@/components/SuChangeOneself/SuChangeOneself";

/** Shown as the product name while no page has set a title yet. */
const PRODUCT_NAME = "Cognosa WebApp";
/** useTopNavBarTitle() builds "<product> / <page>"; the shell shows the two apart. */
const TITLE_SEP = " / ";

const SCHEMES: { value: Scheme; label: string }[] = [
  { value: "light", label: "Light" },
  { value: "dark", label: "Dark" },
  { value: "system", label: "System" },
];

/** A menu entry is a route, or (Change Group only) an action that opens a dialog. */
interface NavItem {
  label: string;
  icon: LucideIcon;
  path?: string;
  action?: "change_group";
}
interface NavGroup {
  id: string;
  label: string;
  items: NavItem[];
}

/**
 * The menu for the logged user. Same conditions as v1.0.1's TopNavBar:
 * Query Documents when logged in (Chat only when chat is on for the group),
 * GroupAdmin for group admins, SuperUser for superusers.
 */
function useNavGroups(): NavGroup[] {
  const isLogged = useLoggedUserStore((s) => s.isLogged);
  const chatEnabled = useLoggedUserStore((s) => s.chat_enabled);
  const isGroupAdmin = useLoggedUserStore((s) => s.is_groupadmin);
  const isSuperuser = useLoggedUserStore((s) => s.is_superuser);
  const groups: NavGroup[] = [];
  if (isLogged) {
    const items: NavItem[] = [
      { label: "Manage Contexts", icon: Layers, path: "/app/manage_contexts" },
      { label: "Queries", icon: Search, path: "/app/query_documents/queries" },
    ];
    if (chatEnabled) {
      items.push({ label: "Chat", icon: MessagesSquare, path: "/app/chat" });
    }
    groups.push({ id: "query_documents", label: "Query Documents", items });
  }
  if (isGroupAdmin) {
    groups.push({
      id: "groupadmin",
      label: "GroupAdmin",
      items: [
        { label: "Users", icon: Users, path: "/app/groupadmin/manage_users" },
        {
          label: "Queries",
          icon: ListChecks,
          path: "/app/groupadmin/manage_queries",
        },
        {
          label: "Retrieval Parameters",
          icon: SlidersHorizontal,
          path: "/app/groupadmin/retrieval_parameters",
        },
        {
          label: "Doc Collections",
          icon: Library,
          path: "/app/groupadmin/manage_vdbs",
        },
      ],
    });
  }
  if (isSuperuser) {
    groups.push({
      id: "superuser",
      label: "SuperUser",
      items: [
        { label: "Change Group", icon: ArrowLeftRight, action: "change_group" },
        { label: "Groups", icon: Building2, path: "/app/su/manage_groups" },
        { label: "Users", icon: UserCog, path: "/app/su/manage_users" },
        { label: "LLMs", icon: Brain, path: "/app/su/manage_llms" },
        { label: "VDBs", icon: Database, path: "/app/su/manage_vdbs" },
        { label: "Doc Tasks", icon: ListTodo, path: "/app/su/manage_doc_tasks" },
        {
          label: "Server Status",
          icon: Activity,
          path: "/app/su/server_status",
        },
        {
          label: "Api Settings",
          icon: KeyRound,
          path: "/app/su/manage_api_settings",
        },
        { label: "Log CRUD", icon: ScrollText, path: "/app/su/manage_log_crud" },
      ],
    });
  }
  return groups;
}

/** True when the item's route is the current page (or a page under it: /app/chat/12). */
function isCurrent(item: NavItem, pathname: string) {
  if (!item.path) return false;
  const here = pathname.replace(/\/+$/, "");
  return here === item.path || here.startsWith(item.path + "/");
}

function BrandMark() {
  return (
    <span className="primary-fill grid size-8 flex-none place-items-center rounded-full">
      <svg
        viewBox="0 0 16 16"
        className="size-4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        aria-hidden
      >
        <path d="M11.6 4.9A4.7 4.7 0 1 0 11.6 11.1" />
        <circle cx="8" cy="8" r="1.1" fill="currentColor" stroke="none" />
      </svg>
    </span>
  );
}

/** The one control that switches between the expanded sidebar and the icon strip. */
function NavToggle() {
  const { state, toggleSidebar } = useSidebar();
  const label =
    state === "expanded" ? "Collapse navigation" : "Expand navigation";
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button
          type="button"
          className="icon-btn size-8!"
          onClick={toggleSidebar}
          aria-label={label}
          aria-expanded={state === "expanded"}
        >
          {state === "expanded" ? (
            <PanelLeftClose className="size-4" />
          ) : (
            <PanelLeftOpen className="size-4" />
          )}
        </button>
      </TooltipTrigger>
      <TooltipContent side="right">{label}</TooltipContent>
    </Tooltip>
  );
}

interface NavGroupProps {
  group: NavGroup;
  pathname: string;
  /** a route was chosen (closes the phone sheet) */
  onPick: () => void;
  /** an action item was chosen */
  onAction: (action: NonNullable<NavItem["action"]>) => void;
}

/** Expanded: a foldable group with its items. */
function NavGroupOpen({ group, pathname, onPick, onAction }: NavGroupProps) {
  const folded = useNav((s) => s.folded.includes(group.id));
  const setFolded = useNav((s) => s.setFolded);
  const holdsCurrent = group.items.some((i) => isCurrent(i, pathname));
  return (
    <Collapsible open={!folded} onOpenChange={(o) => setFolded(group.id, !o)}>
      <SidebarGroup className="px-2 py-1">
        <SidebarGroupLabel asChild>
          <CollapsibleTrigger
            className={cn(
              "group/fold w-full gap-2 hover:bg-tint hover:text-tint-fg",
              holdsCurrent && "text-accent-text"
            )}
          >
            <span className="flex-1 text-left">{group.label}</span>
            <ChevronDown className="transition-transform group-data-[state=closed]/fold:-rotate-90" />
          </CollapsibleTrigger>
        </SidebarGroupLabel>
        <CollapsibleContent>
          <SidebarGroupContent>
            <SidebarMenu className="gap-px">
              {group.items.map((i) => {
                const Icon = i.icon;
                const current = isCurrent(i, pathname);
                return (
                  <SidebarMenuItem key={i.label}>
                    {i.path ? (
                      <SidebarMenuButton asChild isActive={current}>
                        <Link
                          to={i.path}
                          aria-current={current ? "page" : undefined}
                          onClick={onPick}
                        >
                          <Icon />
                          <span>{i.label}</span>
                        </Link>
                      </SidebarMenuButton>
                    ) : (
                      <SidebarMenuButton onClick={() => onAction(i.action!)}>
                        <Icon />
                        <span>{i.label}</span>
                      </SidebarMenuButton>
                    )}
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </CollapsibleContent>
      </SidebarGroup>
    </Collapsible>
  );
}

/** Icon strip: every item of the group as its own icon; the tooltip names group and item. */
function NavGroupStrip({ group, pathname, onPick, onAction }: NavGroupProps) {
  return (
    <>
      {group.items.map((i) => {
        const Icon = i.icon;
        const name = `${group.label}: ${i.label}`;
        const current = isCurrent(i, pathname);
        return (
          <SidebarMenuItem key={i.label}>
            {i.path ? (
              <SidebarMenuButton
                asChild
                isActive={current}
                tooltip={name}
                className="justify-center"
              >
                <Link
                  to={i.path}
                  aria-label={name}
                  aria-current={current ? "page" : undefined}
                  onClick={onPick}
                >
                  <Icon />
                </Link>
              </SidebarMenuButton>
            ) : (
              <SidebarMenuButton
                tooltip={name}
                aria-label={name}
                className="justify-center"
                onClick={() => onAction(i.action!)}
              >
                <Icon />
              </SidebarMenuButton>
            )}
          </SidebarMenuItem>
        );
      })}
    </>
  );
}

function initialsOf(name: string) {
  const words = name.trim().split(/[\s._@-]+/).filter(Boolean);
  if (words.length === 0) return "";
  const first = words[0][0];
  const last = words.length > 1 ? words[words.length - 1][0] : "";
  return (first + last).toUpperCase();
}

function UserMenu({ strip, onPick }: { strip: boolean; onPick: () => void }) {
  const { isMobile } = useSidebar();
  const scheme = useScheme((s) => s.scheme);
  const setScheme = useScheme((s) => s.setScheme);
  const fullName = useLoggedUserStore((s) => s.full_name);
  const userName = useLoggedUserStore((s) => s.user_name);
  const email = useLoggedUserStore((s) => s.email);
  const groupName = useLoggedUserStore((s) => s.group_name);
  const name = fullName || userName || email;
  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu modal={false}>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              tooltip={name}
              aria-label={`User menu: ${name}`}
              className={cn(
                "h-11",
                strip ? "justify-center" : "border border-line bg-surface px-2"
              )}
            >
              <span className="grid size-7 flex-none place-items-center rounded-full bg-tint text-[11px] font-semibold text-tint-fg">
                {initialsOf(name)}
              </span>
              {!strip && (
                <>
                  <span className="min-w-0 flex-1 truncate font-medium text-ink">
                    {name}
                  </span>
                  <ChevronsUpDown className="text-muted-foreground" />
                </>
              )}
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            side={isMobile ? "top" : "right"}
            align="end"
            sideOffset={isMobile ? 6 : 12}
          >
            {strip && (
              <>
                <DropdownMenuLabel>
                  <span className="block text-sm text-ink">{name}</span>
                  <span className="block font-medium">{groupName}</span>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
              </>
            )}
            <DropdownMenuItem asChild>
              <Link to="/app/change_password" onClick={onPick}>
                Change password
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to="/app/logout" onClick={onPick}>
                Logout
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuLabel>Colour scheme</DropdownMenuLabel>
            <DropdownMenuRadioGroup
              value={scheme}
              onValueChange={(v) => setScheme(v as Scheme)}
            >
              {SCHEMES.map((s) => (
                <DropdownMenuRadioItem
                  key={s.value}
                  value={s.value}
                  onSelect={(e) => e.preventDefault()}
                >
                  {s.label}
                </DropdownMenuRadioItem>
              ))}
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}

function AppSidebar() {
  const { pathname } = useLocation();
  const { state, isMobile, setOpenMobile } = useSidebar();
  const groups = useNavGroups();
  const isLogged = useLoggedUserStore((s) => s.isLogged);
  const isSuperuser = useLoggedUserStore((s) => s.is_superuser);
  const groupName = useLoggedUserStore((s) => s.group_name);
  const title = useNavbarStore((s) => s.title);
  const product = title.split(TITLE_SEP)[0] || PRODUCT_NAME;
  const [changeGroupOpen, setChangeGroupOpen] = useState(false);

  const strip = state === "collapsed" && !isMobile;
  const onPick = () => setOpenMobile(false);
  const onAction = () => {
    setOpenMobile(false);
    setChangeGroupOpen(true);
  };
  return (
    <>
      <Sidebar variant="floating" collapsible="icon" aria-label="Navigation">
        <SidebarHeader
          className={cn("gap-2.5 p-2.5 pb-1", strip && "items-center px-0")}
        >
          <div className={cn("flex items-center gap-2", strip && "flex-col")}>
            <Link
              to="/app"
              onClick={onPick}
              title={strip ? `${product} (${groupName})` : undefined}
              className="flex min-w-0 flex-1 items-center gap-2 rounded-full font-heading text-base font-semibold tracking-[-0.01em] text-ink no-underline"
            >
              <BrandMark />
              <span className={cn("truncate", strip && "sr-only")}>
                {product}
              </span>
            </Link>
            {!isMobile && <NavToggle />}
          </div>
          {!strip && groupName && (
            <div
              className="rounded-xl bg-tint px-3 py-1.5 text-[13px] leading-snug font-medium text-tint-fg"
              title="Your group"
            >
              {groupName}
            </div>
          )}
        </SidebarHeader>
        <SidebarContent
          className="scroll-soft group-data-[collapsible=icon]:overflow-y-auto"
          role="navigation"
          aria-label="Main"
        >
          {strip ? (
            <SidebarGroup className="pt-2">
              <SidebarMenu className="items-center gap-1">
                {groups.map((g, n) => (
                  <Fragment key={g.id}>
                    {n > 0 && <SidebarSeparator className="mx-0 my-1 w-6" />}
                    <NavGroupStrip
                      group={g}
                      pathname={pathname}
                      onPick={onPick}
                      onAction={onAction}
                    />
                  </Fragment>
                ))}
              </SidebarMenu>
            </SidebarGroup>
          ) : (
            groups.map((g) => (
              <NavGroupOpen
                key={g.id}
                group={g}
                pathname={pathname}
                onPick={onPick}
                onAction={onAction}
              />
            ))
          )}
        </SidebarContent>
        {isLogged && (
          <SidebarFooter className={cn("p-2.5", strip && "items-center px-0")}>
            <UserMenu strip={strip} onPick={onPick} />
          </SidebarFooter>
        )}
      </Sidebar>
      {/* Mounted with the SuperUser group, as the menu item was in v1.0.1 */}
      {isSuperuser && (
        <SuChangeOneself show={changeGroupOpen} onShowChange={setChangeGroupOpen} />
      )}
    </>
  );
}

/**
 * The page name as a heading, at the top of every page. On a phone it carries the
 * button that opens the navigation. Children are page tools placed after the name.
 *
 * The name is, in this order: the `title` prop; the page part of what the page
 * passed to useTopNavBarTitle() ("Manage Users" of "Cognosa WebApp / Manage Users");
 * the label of the current page's menu item.
 */
export function PageHead({
  title,
  children,
  className,
}: {
  title?: string;
  children?: ReactNode;
  className?: string;
}) {
  const { pathname } = useLocation();
  const { isMobile, toggleSidebar, openMobile } = useSidebar();
  const storeTitle = useNavbarStore((s) => s.title);
  const groups = useNavGroups();
  // Heading = the menu label of the current page (ruling of 2026-11-22); the
  // v1.0.1 title still names the browser tab and is the fallback here.
  let name = title;
  if (name === undefined) {
    for (const g of groups) {
      for (const i of g.items) if (isCurrent(i, pathname)) name = i.label;
    }
  }
  if (!name) {
    name = storeTitle.split(TITLE_SEP).slice(1).join(TITLE_SEP);
  }
  return (
    <div className={cn("flex min-h-10 flex-none items-center gap-2", className)}>
      {isMobile && (
        <button
          type="button"
          className="icon-btn"
          aria-label="Open navigation"
          aria-expanded={openMobile}
          onClick={toggleSidebar}
        >
          <Menu className="size-[18px]" />
        </button>
      )}
      <h1 className="flex-none font-heading text-[22px] leading-none font-semibold tracking-[-0.015em] text-ink max-md:text-lg">
        {name}
      </h1>
      {children}
    </div>
  );
}

export function Shell({ children }: { children: ReactNode }) {
  const open = useNav((s) => s.open);
  const setOpen = useNav((s) => s.setOpen);
  const title = useNavbarStore((s) => s.title);
  return (
    <SidebarProvider
      open={open}
      onOpenChange={setOpen}
      className="h-dvh min-h-0"
      style={
        {
          "--sidebar-width": "256px",
          "--sidebar-width-icon": "44px",
        } as React.CSSProperties
      }
    >
      <title>{title}</title>
      <AppSidebar />
      <SidebarInset className="min-h-0 min-w-0 bg-transparent">
        <div className="scroll-soft min-h-0 flex-1 overflow-auto">{children}</div>
      </SidebarInset>
    </SidebarProvider>
  );
}
