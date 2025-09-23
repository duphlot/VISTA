import * as universal_hooks from '../../../src/hooks.ts';

export { matchers } from './matchers.js';

export const nodes = [
	() => import('./nodes/0'),
	() => import('./nodes/1'),
	() => import('./nodes/2'),
	() => import('./nodes/3'),
	() => import('./nodes/4'),
	() => import('./nodes/5'),
	() => import('./nodes/6'),
	() => import('./nodes/7'),
	() => import('./nodes/8'),
	() => import('./nodes/9'),
	() => import('./nodes/10'),
	() => import('./nodes/11'),
	() => import('./nodes/12'),
	() => import('./nodes/13'),
	() => import('./nodes/14'),
	() => import('./nodes/15'),
	() => import('./nodes/16'),
	() => import('./nodes/17'),
	() => import('./nodes/18'),
	() => import('./nodes/19'),
	() => import('./nodes/20'),
	() => import('./nodes/21'),
	() => import('./nodes/22'),
	() => import('./nodes/23')
];

export const server_loads = [];

export const dictionary = {
		"/": [6],
		"/assistants": [8],
		"/assistant/[assistantId]": [7],
		"/conversation/[id]": [9],
		"/models": [10],
		"/models/[...model]": [11],
		"/privacy": [12],
		"/r/[id]": [13],
		"/settings/(nav)": [14,[2,3]],
		"/settings/(nav)/application": [16,[2,3]],
		"/settings/(nav)/assistants/new": [19,[2,3]],
		"/settings/(nav)/assistants/[assistantId]": [17,[2,3]],
		"/settings/(nav)/assistants/[assistantId]/edit": [18,[2,3]],
		"/settings/(nav)/[...model]": [15,[2,3]],
		"/tools": [20,[4]],
		"/tools/new": [23,[4]],
		"/tools/[toolId]": [21,[4,5]],
		"/tools/[toolId]/edit": [22,[4,5]]
	};

export const hooks = {
	handleError: (({ error }) => { console.error(error) }),
	
	reroute: universal_hooks.reroute || (() => {}),
	transport: universal_hooks.transport || {}
};

export const decoders = Object.fromEntries(Object.entries(hooks.transport).map(([k, v]) => [k, v.decode]));

export const hash = false;

export const decode = (type, value) => decoders[type](value);

export { default as root } from '../root.js';