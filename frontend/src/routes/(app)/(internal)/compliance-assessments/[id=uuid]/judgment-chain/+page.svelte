<script lang="ts">
	import { m } from '$paraglide/messages';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const chain = $derived(data.chain);

	let expanded = $state<Record<string, boolean>>({});

	const stageLabel: Record<string, () => string> = {
		REALITY_CANDIDATE: m.jcStageReality,
		TRACE_CANDIDATE: m.jcStageTrace,
		DEFINED_LOCUS: m.jcStageLocus,
		DOMAIN_CONTRACT: m.jcStageDomain,
		CLAIM_CANDIDATE: m.jcStageClaim,
		RELATION_CANDIDATE: m.jcStageRelation,
		EVIDENCE_BINDING: m.jcStageEvidence,
		RANK_ASSIGNMENT: m.jcStageRank,
		RESIDUAL_AUDIT: m.jcStageResiduals,
		JUDGMENT_CANDIDATE: m.jcStageJudgment,
		ACTION_LICENSE: m.jcStageAction,
		HANDOFF: m.jcStageHandoff,
		FEEDBACK_TRACE: m.jcStageFeedback,
		REALITY_REEVALUATION: m.jcStageReevaluation
	};

	function label(stage: string): string {
		return stageLabel[stage] ? stageLabel[stage]() : stage;
	}

	const stateClass: Record<string, string> = {
		reached: 'bg-emerald-500',
		blocked: 'bg-red-500',
		not_reached: 'bg-surface-300'
	};

	const routeLabel: Record<string, () => string> = {
		AUTOMATION: m.jcRouteAutomation,
		DEFERRAL_QUEUE: m.jcRouteDeferral,
		HUMAN_REVIEW: m.jcRouteHumanReview
	};
</script>

<div class="flex flex-col gap-6 p-4">
	<header class="flex flex-col gap-1">
		<h1 class="text-2xl font-bold">{m.jcTitle()}</h1>
		<p class="text-sm text-surface-600">
			{chain.compliance_assessment.name} · {chain.compliance_assessment.framework.name} ·
			{chain.compliance_assessment.folder.name}
		</p>
		<p class="text-sm">{m.jcIntro()}</p>
		<a class="anchor text-sm" href="/compliance-assessments/{chain.compliance_assessment.id}">
			{m.jcBackToAssessment()}
		</a>
	</header>

	<section class="grid grid-cols-1 gap-3 md:grid-cols-3" aria-label={m.jcCounts()}>
		<div class="card p-3">
			<h2 class="text-sm font-semibold">{m.jcByJudgment()}</h2>
			<ul class="text-sm">
				{#each Object.entries(chain.counts.by_judgment_status) as [k, v]}
					<li><span class="font-mono">{k}</span>: {v}</li>
				{/each}
			</ul>
		</div>
		<div class="card p-3">
			<h2 class="text-sm font-semibold">{m.jcByFailedStage()}</h2>
			<ul class="text-sm">
				{#each Object.entries(chain.counts.by_failed_stage) as [k, v]}
					<li>{k === 'NONE' ? m.jcNoFailedStage() : label(k)}: {v}</li>
				{/each}
			</ul>
		</div>
		<div class="card p-3">
			<h2 class="text-sm font-semibold">{m.jcByRoute()}</h2>
			<ul class="text-sm">
				{#each Object.entries(chain.counts.by_handoff_route) as [k, v]}
					<li>{routeLabel[k] ? routeLabel[k]() : k}: {v}</li>
				{/each}
			</ul>
			<p class="mt-2 text-xs text-surface-600">
				{m.jcActionThreshold({ rank: chain.action_minimum_rank })}
			</p>
		</div>
	</section>

	<section class="card p-3 text-xs">
		<h2 class="text-sm font-semibold">{m.jcLegend()}</h2>
		<div class="flex flex-wrap gap-2">
			{#each chain.stages as stage, i}
				<span class="rounded bg-surface-200 px-2 py-0.5">{i + 1}. {label(stage)}</span>
			{/each}
		</div>
	</section>

	<section class="overflow-x-auto">
		<table class="table w-full text-sm">
			<thead>
				<tr>
					<th>{m.jcRequirement()}</th>
					<th>{m.jcStages()}</th>
					<th>{m.jcJudgment()}</th>
					<th>{m.jcRank()}</th>
					<th>{m.jcRoute()}</th>
					<th>{m.jcDeclaredResult()}</th>
				</tr>
			</thead>
			<tbody>
				{#each chain.requirements as row (row.requirement.id)}
					<tr>
						<td>
							<button
								type="button"
								class="anchor text-start"
								aria-expanded={!!expanded[row.requirement.id]}
								onclick={() => (expanded[row.requirement.id] = !expanded[row.requirement.id])}
							>
								<span class="font-mono">{row.requirement.ref_id ?? ''}</span>
								{row.requirement.name ?? ''}
							</button>
						</td>
						<td>
							<div class="flex gap-0.5" title={label(row.judgment.failed_stage ?? '')}>
								{#each row.stages as s}
									<span
										class="h-3 w-3 rounded-sm {stateClass[s.state]}"
										aria-label="{label(s.stage)}: {s.state}"
									></span>
								{/each}
							</div>
						</td>
						<td class="font-mono">{row.judgment.status}</td>
						<td class="font-mono">{row.judgment.rank} / {row.judgment.rank_ceiling}</td>
						<td
							>{row.handoff
								? routeLabel[row.handoff.route]
									? routeLabel[row.handoff.route]()
									: row.handoff.route
								: '—'}</td
						>
						<td class="text-surface-600"
							>{row.declared_result} <span class="text-xs">({m.jcDeclarationNote()})</span></td
						>
					</tr>
					{#if expanded[row.requirement.id]}
						<tr>
							<td colspan="6" class="bg-surface-100 p-3">
								<div class="grid grid-cols-1 gap-3 md:grid-cols-2">
									<div>
										<h3 class="font-semibold">{m.jcResiduals()}</h3>
										{#if row.residuals.length === 0}
											<p class="text-xs">{m.jcNoResiduals()}</p>
										{:else}
											<ul class="text-xs">
												{#each row.residuals as r}
													<li>
														<span class="font-mono">{r.code}</span>
														<span class="text-surface-600"
															>({label(r.failed_stage)}{r.blocking
																? ''
																: `, ${m.jcNonBlocking()}`})</span
														>
														— {r.description}
													</li>
												{/each}
											</ul>
										{/if}
										{#if row.handoff}
											<p class="mt-2 text-xs">{m.jcHandoffRationale()}: {row.handoff.rationale}</p>
										{/if}
									</div>
									<div>
										<h3 class="font-semibold">{m.jcEvidence()}</h3>
										{#if row.evidence.length === 0}
											<p class="text-xs">{m.jcNoEvidence()}</p>
										{:else}
											<ul class="text-xs">
												{#each row.evidence as ev}
													<li>
														{ev.name} · {ev.status} · {ev.owner || m.jcNoOwner()} · {ev.freshness ||
															'—'}
														{#if ev.became_trace}
															<span class="text-emerald-700">({m.jcBecameTrace()})</span>
														{:else}
															<span class="text-red-700 font-mono">({ev.reason})</span>
														{/if}
													</li>
												{/each}
											</ul>
										{/if}
									</div>
								</div>
							</td>
						</tr>
					{/if}
				{/each}
			</tbody>
		</table>
	</section>
</div>
