import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "cn"
import { Slot } from "radix-ui"

const buttonVariants = cva(
  "group/button inline-flex shrink-0 items-center justify-center rounded-full border border-transparent bg-clip-padding text-sm font-semibold whitespace-nowrap transition-all outline-none select-none focus-visible:ring-3 focus-visible:ring-ring/40 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring active:not-aria-[haspopup]:translate-y-px disabled:cursor-not-allowed disabled:opacity-55 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        // the gradient pill; fill and text colour come from --primary-fill / --primary-foreground
        default: "primary-fill border-0 hover:not-disabled:brightness-110",
        outline:
          "border-line bg-surface text-ink hover:not-disabled:border-tint-edge hover:not-disabled:text-accent-text aria-expanded:border-tint-edge",
        secondary:
          "border-hair bg-tint text-tint-fg hover:not-disabled:border-tint-edge",
        ghost: "text-ink-2 hover:not-disabled:bg-tint hover:not-disabled:text-tint-fg aria-expanded:bg-tint aria-expanded:text-tint-fg",
        destructive:
          "bg-err-bg text-err hover:not-disabled:brightness-95",
        link: "text-accent-text underline underline-offset-4",
      },
      size: {
        default: "h-[34px] gap-1.5 px-3.5",
        xs: "h-7 gap-1 px-2.5 text-[13px]",
        sm: "h-8 gap-1.5 px-3 text-[13px]",
        lg: "h-[42px] gap-2 px-5 text-[14.5px]",
        icon: "size-9",
        "icon-xs": "size-6 [&_svg:not([class*='size-'])]:size-3.5",
        "icon-sm": "size-[30px]",
        "icon-lg": "size-[52px] [&_svg:not([class*='size-'])]:size-[22px]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot.Root : "button"

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
