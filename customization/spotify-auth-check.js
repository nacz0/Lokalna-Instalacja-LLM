/**
 * Spotify Authentication Check
 * Sprawdza czy uzytkownik jest zalogowany na Spotify
 */

(function() {
  'use strict';

  const SPOTIFY_API_ENDPOINT = '/api/v1/pipelines/spotify_search/status';
  
  // Sprawdz status Spotify przy starcie
  async function checkSpotifyStatus() {
    try {
      // Proba pobrania statusu z API (gdy bedzie dostepne)
      console.log('[Spotify] Checking authentication status...');
      
      // Alternatywnie: sprawdz localStorage
      const spotifyData = localStorage.getItem('spotify_token');
      if (spotifyData) {
        const data = JSON.parse(spotifyData);
        if (data.access_token) {
          console.log('[Spotify] User is logged in');
          return true;
        }
      }
      
      console.log('[Spotify] User is NOT logged in');
      return false;
    } catch (e) {
      console.warn('[Spotify] Error checking status:', e);
      return false;
    }
  }

  // Obserwuj gdy uzytkownik kliknie na Spotify pipeline
  function observeSpotifyPipelineClick() {
    document.addEventListener('click', async (e) => {
      const target = e.target.closest('[class*="spotify"], [data-pipeline*="spotify"]');
      
      if (target) {
        console.log('[Spotify] User clicked on Spotify pipeline');
        
        const isLoggedIn = await checkSpotifyStatus();
        
        if (!isLoggedIn) {
          e.preventDefault();
          e.stopPropagation();
          
          showSpotifyLoginModal();
          return false;
        }
      }
    }, true);
  }

  // Pokaz modal z instrukcjami logowania
  function showSpotifyLoginModal() {
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
      background: #1a1a2e;
      color: white;
      padding: 30px;
      border-radius: 10px;
      max-width: 500px;
      box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
      text-align: center;
    `;

    content.innerHTML = `
      <h2 style="color: #4CAF50; margin-bottom: 20px;">Spotify Login Required</h2>
      <p style="margin-bottom: 20px; line-height: 1.6;">
        To use the Spotify Search feature, you need to authenticate first.
      </p>
      <div style="background: #0f0f1a; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: left;">
        <p><strong>Follow these steps:</strong></p>
        <ol style="text-align: left; margin: 10px 0;">
          <li>Open PowerShell</li>
          <li>Run: <code style="background: #16213e; padding: 5px;">cd integrations && .\\spotify_auth_setup.ps1</code></li>
          <li>Choose option 1 to login</li>
          <li>Go back to this page and refresh</li>
        </ol>
      </div>
      <div style="display: flex; gap: 10px;">
        <button id="spotify-close-btn" style="
          flex: 1;
          padding: 10px;
          background: #667eea;
          border: none;
          color: white;
          border-radius: 5px;
          cursor: pointer;
          font-size: 14px;
        ">Close</button>
        <button id="spotify-refresh-btn" style="
          flex: 1;
          padding: 10px;
          background: #4CAF50;
          border: none;
          color: white;
          border-radius: 5px;
          cursor: pointer;
          font-size: 14px;
        ">Refresh</button>
      </div>
    `;

    modal.appendChild(content);
    document.body.appendChild(modal);

    document.getElementById('spotify-close-btn').onclick = () => {
      modal.remove();
    };

    document.getElementById('spotify-refresh-btn').onclick = () => {
      window.location.reload();
    };
  }

  // Inicjalizacja
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      observeSpotifyPipelineClick();
    });
  } else {
    observeSpotifyPipelineClick();
  }

  console.log('[Spotify] Authentication check initialized');
})();
