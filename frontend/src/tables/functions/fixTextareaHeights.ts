export function fixTextareaHeights(tbody: HTMLElement) {
  const rows = tbody.querySelectorAll("tr");
  rows.forEach((row) => {
    if (!row.querySelector(".need-fix-height")) return;
    const textareas = row.querySelectorAll<HTMLTextAreaElement>("textarea");
    if (!textareas.length) return;
    // reset first
    textareas.forEach((t) => {
      t.style.height = "auto";
    });
    let maxHeight = 0;
    row.querySelectorAll("td").forEach((td) => {
      maxHeight = Math.max(maxHeight, td.offsetHeight);
    });
    textareas.forEach((t) => {
      t.style.height = `${maxHeight}px`;
    });
  });
}
