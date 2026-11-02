import { BASE_API_URL } from '$lib/utils/constants';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = (async ({ fetch, params }) => {
	const endpoint = `${BASE_API_URL}/compliance-assessments/${params.id}/judgment_chain/`;
	const res = await fetch(endpoint);
	if (!res.ok) {
		throw error(res.status, res.statusText || 'Failed to load the judgment chain');
	}
	const chain = await res.json();
	return { chain };
}) satisfies PageServerLoad;
