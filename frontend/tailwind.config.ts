import type { Config } from "tailwindcss";

export default {
  content: ["./**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#ff8800",
      },
    },
  },
  plugins: [],
} satisfies Config;
