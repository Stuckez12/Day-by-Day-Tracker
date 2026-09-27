import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
import simpleImportSort from 'eslint-plugin-simple-import-sort';
const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,

  {
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "warn",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
        },
      ],
      'simple-import-sort/imports': 'error',
    },
    plugins: {
      'simple-import-sort': simpleImportSort,
    },
  },
  

  globalIgnores([
    ".next/**",
    "out/**",
    "build/**",
    "tests/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
