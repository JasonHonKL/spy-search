import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // I hate this folder structure but the .env file is in the parent directory
  const env = loadEnv(mode, process.cwd() + "/../");
  const port = Number(`${env.VITE_PORT ?? '8080'}`);
  return {
    server: {
      host: "::",
      port: port,
    },
    plugins: [
      react(),
      mode === 'development' &&
      componentTagger(),
    ].filter(Boolean),
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
  }
});
