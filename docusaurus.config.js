module.exports = {
  title: "Netsage Dashboard Documentation",
  tagline: "Netsage Dashboard Documentation",
  url: "https://netsage-project.github.io",
  baseUrl: "/netsage-grafana-configs/",
  favicon: "img/favicon.ico",
  organizationName: "netsage-project", // Usually your GitHub org/user name.
  projectName: "netsage-grafana-configs", // Usually your repo name.
  themeConfig: {
    navbar: {
      title: "NetSage Documentation",
      logo: {
        alt: "NetSage Logo",
        src: "img/logo.png",
      },
      items: [
        {
          to: "docs/develop",
          activeBasePath: "docs",
          label: "Developer",
          position: "left",
        },
        {
          href: "https://netsage-project.github.io/netsage-pipeline/",
          label: "Pipeline Documentation",
          position: "left",
        },
        // {to: 'blog', label: 'Blog', position: 'left'},
        {
          href: "https://github.com/netsage-project/netsage-grafana-configs",
          label: "GitHub",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [],
      copyright: `Copyright © ${new Date().getFullYear()} NetSage Built with Docusaurus.`,
    },
  },
  presets: [
    [
      "@docusaurus/preset-classic",
      {
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          // Please change this to your repo.
          editUrl:
            "https://github.com/netsage-project/netsage-grafana-configs/edit/1.5.2/",
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      },
    ],
  ],
};
