import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f2f6ff",
          100: "#e3ebff",
          200: "#c3d3ff",
          300: "#9bb2ff",
          400: "#6d87fb",
          500: "#4a63ee",
          600: "#3748d1",
          700: "#2c39a8",
          800: "#263184",
          900: "#232c68",
        },
        ink: {
          900: "#0b1020",
          800: "#151b2e",
          700: "#212840",
          600: "#333c5c",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px -12px rgba(15, 23, 42, 0.12)",
      },
    },
  },
  plugins: [],
};
export default config;
