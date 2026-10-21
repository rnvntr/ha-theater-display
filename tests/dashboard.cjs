const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const yaml = fs.readFileSync(path.join(__dirname, '../home-assistant/dashboard.yaml'), 'utf8');
const js = yaml.split('[[[')[1].split(']]]')[0];
const render = new Function('states', 'variables', js);
const variables = {players: ['media_player.first', 'media_player.second'], poster_files: []};
const player = (state, title) => ({state, attributes: {media_title: title, media_duration: 600, media_position: 60}});
assert.match(render({}, variables), /THEATER/);
assert.doesNotMatch(render({}, variables), /undefined|NaN/);
for (const state of ['playing', 'buffering', 'paused']) {
  const html = render({'media_player.first': player(state, '<First>')}, variables);
  assert.match(html, /&lt;First&gt;/);
  assert.doesNotMatch(html, /<First>/);
}
const html = render({
  'media_player.first': player('paused', 'Paused title'),
  'media_player.second': player('playing', 'Playing title'),
  'media_player.unrelated': player('playing', 'Other room')
}, variables);
assert.match(html, /Playing title/);
assert.doesNotMatch(html, /Paused title|Other room/);
assert.match(render({}, {...variables, poster_files: ['example poster.jpg']}), /example%20poster.jpg/);
assert.doesNotMatch(render({'media_player.first': player('unavailable', 'Offline title')}, variables), /Offline title/);
console.log('Dashboard rendering checks passed');
