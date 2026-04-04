export type SiteConfig = typeof siteConfig;

export const siteConfig = {
  name: "My App",
  description: "My app description.",
  navItems: [
    { label: "Home", href: "/" },
  ],
  navMenuItems: [
    { label: "Dashboard", href: "/dashboard" },
    { label: "Profile", href: "/profile" },
    { label: "Logout", href: "/logout" },
  ],
  links: {
    github: "https://github.com/your-org/your-repo",
    twitter: "",
    docs: "/",
    discord: "",
    sponsor: "",
  },
};
