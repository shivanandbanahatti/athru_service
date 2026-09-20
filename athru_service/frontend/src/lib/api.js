/** Thin Frappe call wrapper for desk + website sessions */
export async function call(method, args = {}) {
  if (window.frappe?.call) {
    const r = await window.frappe.call({ method, args });
    return r.message;
  }
  const res = await fetch("/api/method/" + method, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": window.csrf_token || "",
    },
    body: JSON.stringify(args),
    credentials: "include",
  });
  const data = await res.json();
  if (data.exc) throw new Error(data.exc);
  return data.message;
}

export function deskUrl(doctype, name) {
  const slug = doctype.toLowerCase().replace(/ /g, "-");
  return name ? `/app/${slug}/${encodeURIComponent(name)}` : `/app/${slug}`;
}
