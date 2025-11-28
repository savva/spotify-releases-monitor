<template>
  <main class="container">
    <header>
      <h1>Spotify Releases Monitor</h1>
      <p>Track your listening history and manage playlists in one place.</p>
    </header>

    <section v-if="!isAuthenticated" class="panel">
      <h2>Connect your Spotify</h2>
      <p>Sign in with Spotify to start exploring your recent tracks.</p>
      <button class="primary" @click="loginWithSpotify">Log in with Spotify</button>
    </section>

    <section v-else class="panel">
      <div class="user-card">
        <img v-if="user?.avatar_url" :src="user?.avatar_url" alt="Avatar" />
        <div>
          <p class="subtitle">Signed in as</p>
          <h2>{{ user?.display_name ?? user?.email ?? user?.spotify_user_id }}</h2>
          <p v-if="user?.email">{{ user?.email }}</p>
        </div>
        <button class="ghost" @click="logout">Log out</button>
      </div>

      <div class="actions">
        <button class="primary" @click="loadRecentTracks" :disabled="recentLoading">
          {{ recentLoading ? 'Loading…' : 'Refresh recent tracks' }}
        </button>
      </div>

      <section class="recent" v-if="recentTracks">
        <h3>Recent listening</h3>
        <ul>
          <li v-for="item in recentTracks.items" :key="item.played_at" class="track">
            <div>
              <p class="track-name">{{ item.track.name }}</p>
              <p class="track-meta">{{ formatArtists(item.track.artists) }} • {{ item.track.album.name }}</p>
            </div>
            <a
              v-if="item.track.external_urls?.spotify"
              :href="item.track.external_urls?.spotify"
              target="_blank"
              rel="noreferrer"
            >
              Open
            </a>
          </li>
        </ul>
      </section>

      <section class="panel">
        <h3>Playlist refresh</h3>
        <form @submit.prevent="loadPlaylistPreview" class="playlist-form">
          <label>
            Playlist link or ID
            <input v-model="playlistLink" placeholder="https://open.spotify.com/playlist/…" required />
          </label>
          <div class="actions gap">
            <button class="primary" type="submit" :disabled="playlistLoading">
              {{ playlistLoading ? 'Loading…' : 'Load playlist' }}
            </button>
            <button
              class="ghost"
              type="button"
              :disabled="playlistRefreshing"
              @click="refreshPlaylist"
            >
              {{ playlistRefreshing ? 'Refreshing…' : 'Refresh playlist' }}
            </button>
          </div>
        </form>

        <p v-if="playlistStatus" class="message success">{{ playlistStatus }}</p>

        <div v-if="playlistData" class="playlist-details">
          <div class="playlist-header">
            <div>
              <p class="subtitle">Playlist</p>
              <h4>{{ playlistData.name || playlistData.playlist_id }}</h4>
            </div>
            <span class="badge">Tracks: {{ playlistData.tracks.length }}</span>
          </div>
          <ul class="playlist-tracks">
            <li v-for="track in playlistData.tracks" :key="track.id" class="track">
              <div>
                <p class="track-name">{{ track.name }}</p>
                <p class="track-meta">
                  {{ (track.artists || []).join(', ') }} <span v-if="track.album">• {{ track.album }}</span>
                </p>
              </div>
              <span class="track-popularity" v-if="track.popularity != null">Pop {{ track.popularity }}</span>
            </li>
          </ul>
        </div>
      </section>

      <section class="panel">
        <h3>Add tracks to playlist</h3>
        <form @submit.prevent="addTracks">
          <label>
            Playlist ID
            <input v-model="playlistId" placeholder="e.g. 37i9dQZF1DXcBWIGoYBM5M" required />
          </label>
          <label>
            Track URIs (comma or newline separated)
            <textarea
              v-model="trackUris"
              rows="3"
              placeholder="spotify:track:..."
              required
            ></textarea>
          </label>
          <button class="primary" type="submit" :disabled="addLoading">
            {{ addLoading ? 'Adding…' : 'Add tracks' }}
          </button>
        </form>
      </section>
    </section>

    <p v-if="message" class="message success">{{ message }}</p>
    <p v-if="error" class="message error">{{ error }}</p>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { apiClient, getApiBaseUrl, resolveErrorMessage } from './lib/api';
import type {
  PlaylistAddResponse,
  PlaylistPreviewResponse,
  RecentTracksResponse,
  User,
} from './lib/types';

const user = ref<User | null>(null);
const recentTracks = ref<RecentTracksResponse | null>(null);
const playlistId = ref('');
const trackUris = ref('');
const playlistLink = ref('');
const message = ref('');
const error = ref('');
const addLoading = ref(false);
const recentLoading = ref(false);
const playlistLoading = ref(false);
const playlistRefreshing = ref(false);
const playlistData = ref<PlaylistPreviewResponse | null>(null);
const playlistStatus = ref('');

const apiBase = getApiBaseUrl();

const isAuthenticated = computed(() => Boolean(user.value));

async function fetchCurrentUser() {
  try {
    const { data } = await apiClient.get<User>('/me');
    user.value = data;
    error.value = '';
  } catch (err) {
    user.value = null;
    if (err instanceof Error) {
      console.warn('Failed to fetch /me', err);
    }
  }
}

function loginWithSpotify() {
  window.location.href = `${apiBase}/auth/login`;
}

async function logout() {
  try {
    await apiClient.post('/auth/logout');
  } catch (err) {
    error.value = resolveErrorMessage(err);
  } finally {
    user.value = null;
    recentTracks.value = null;
  }
}

async function loadRecentTracks() {
  if (!isAuthenticated.value) return;
  recentLoading.value = true;
  try {
    const { data } = await apiClient.get<RecentTracksResponse>('/spotify/recent');
    recentTracks.value = data;
    error.value = '';
  } catch (err) {
    error.value = resolveErrorMessage(err);
  } finally {
    recentLoading.value = false;
  }
}

function normalizeUris() {
  return trackUris
    .value
    .split(/\s|,/)
    .map((uri) => uri.trim())
    .filter(Boolean);
}

async function addTracks() {
  const uris = normalizeUris();
  if (!uris.length) {
    error.value = 'Provide at least one track URI';
    return;
  }
  addLoading.value = true;
  error.value = '';
  try {
    const { data } = await apiClient.post<PlaylistAddResponse>(
      '/spotify/playlists/' + playlistId.value + '/add',
      { uris },
    );
    message.value = `Snapshot ${data.snapshot_id} created`;
    trackUris.value = '';
  } catch (err) {
    error.value = resolveErrorMessage(err);
  } finally {
    addLoading.value = false;
  }
}

function formatArtists(artists: { name: string }[]) {
  return artists.map((artist) => artist.name).join(', ');
}

async function loadPlaylistPreview() {
  if (!playlistLink.value.trim()) {
    error.value = 'Enter a playlist link or ID';
    return;
  }
  playlistLoading.value = true;
  playlistStatus.value = '';
  try {
    const { data } = await apiClient.post<PlaylistPreviewResponse>('/spotify/playlists/preview', {
      playlist_url: playlistLink.value.trim(),
    });
    playlistData.value = data;
    error.value = '';
  } catch (err) {
    error.value = resolveErrorMessage(err);
  } finally {
    playlistLoading.value = false;
  }
}

async function refreshPlaylist() {
  if (!playlistLink.value.trim()) {
    error.value = 'Enter a playlist link or ID';
    return;
  }
  playlistRefreshing.value = true;
  try {
    const { data } = await apiClient.post<PlaylistPreviewResponse>('/spotify/playlists/refresh', {
      playlist_url: playlistLink.value.trim(),
    });
    playlistData.value = data;
    playlistStatus.value = `Removed ${data.removed} listened tracks, added ${data.added} new ones`;
    error.value = '';
  } catch (err) {
    error.value = resolveErrorMessage(err);
  } finally {
    playlistRefreshing.value = false;
  }
}

onMounted(async () => {
  await fetchCurrentUser();
  if (isAuthenticated.value) {
    await loadRecentTracks();
  }
});
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem 4rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

header {
  text-align: center;
}

.panel {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.4);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-card img {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
}

.subtitle {
  margin: 0;
  color: #94a3b8;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.actions.gap {
  gap: 0.75rem;
}

button.primary {
  background: #22c55e;
  padding: 0.75rem 1.5rem;
  border-radius: 999px;
  color: #0f172a;
  font-weight: 600;
}

button.ghost {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 999px;
  color: #f1f5f9;
}

form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

input,
textarea {
  width: 100%;
  padding: 0.75rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(15, 23, 42, 0.75);
  color: #e2e8f0;
}

.recent ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.track {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.65);
}

.playlist-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.playlist-details {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.playlist-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.badge {
  background: rgba(255, 255, 255, 0.08);
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.9rem;
}

.playlist-tracks {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.track-popularity {
  font-size: 0.85rem;
  color: #cbd5e1;
}

.track-name {
  margin: 0;
  font-weight: 600;
}

.track-meta {
  margin: 0;
  color: #94a3b8;
  font-size: 0.9rem;
}

.message {
  text-align: center;
  font-weight: 600;
}

.message.success {
  color: #4ade80;
}

.message.error {
  color: #f87171;
}
</style>
