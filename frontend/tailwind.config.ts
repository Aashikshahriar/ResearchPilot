import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
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
        accent: {
          50: "#fdf4ff",
          100: "#fae8ff",
          200: "#f3caff",
          300: "#eb9dff",
          400: "#dd66fb",
          500: "#c53ce6",
          600: "#a324c2",
          700: "#831c9c",
          800: "#6b1a7d",
          900: "#591866",
        },
        teal: {
          50: "#effefb",
          100: "#c7fdf1",
          200: "#90fae3",
          300: "#53efd3",
          400: "#22d8bd",
          500: "#0abda3",
          600: "#059685",
          700: "#08776c",
          800: "#0b5e57",
          900: "#0d4d48",
        },
        amber: {
          50: "#fffbea",
          100: "#fff3c4",
          200: "#ffe589",
          300: "#ffd24d",
          400: "#ffbe22",
          500: "#f99b0a",
          600: "#dd7606",
          700: "#b7540a",
          800: "#94420f",
          900: "#7a3710",
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
      backgroundImage: {
        "brand-gradient": "linear-gradient(135deg, #4a63ee 0%, #c53ce6 55%, #0abda3 100%)",
        "hero-glow": "radial-gradient(circle at 30% 20%, rgba(74,99,238,0.18), transparent 55%), radial-gradient(circle at 80% 0%, rgba(197,60,230,0.14), transparent 50%)",
      },
    },
  },
  plugins: [],
};
export default config;
