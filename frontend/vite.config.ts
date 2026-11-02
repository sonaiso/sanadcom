import { paraglideVitePlugin } from '@inlang/paraglide-js';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
	plugins: [
		paraglideVitePlugin({
			project: './project.inlang',
			outdir: './src/paraglide',
			outputStructure: 'locale-modules',
			cookieName: 'LOCALE',
			strategy: ['custom-userPreference', 'cookie', 'custom-fallback', 'baseLocale']
		}),
		tailwindcss(),
		sveltekit()
	],
	build: {
		sourcemap: false,
		// Svelte 5 runes output (`const [$$stores, $$cleanup] = setup_stores()`) cannot be
		// down-levelled to the Vite default es2020 target by esbuild; es2022 is supported by
		// every browser the app targets.
		target: 'es2022'
	},
	test: {
		include: ['{src}/**/*.{test,spec}.{js,ts}']
	}
});
