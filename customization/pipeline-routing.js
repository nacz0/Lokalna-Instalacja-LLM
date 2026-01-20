/**
 * Pipeline Routing Script
 * Zmienia URL na /index/{pipeline-name} gdy zmienisz pipeline
 */

(function() {
  'use strict';

  let lastModel = '';

  // Aktualizuj URL na podstawie wybranego modelu/pipeline'u
  const updateUrlWithModel = (modelName) => {
    if (!modelName || modelName === lastModel) return;

    lastModel = modelName;

    // Oczyść i znormalizuj nazwę
    const cleanName = modelName
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9-_./]/g, '_')
      .replace(/\s+/g, '_');

    const newUrl = `/index/${cleanName}`;
    
    // Aktualizuj URL bez przeładowania strony
    window.history.replaceState(
      { model: cleanName },
      `Pipeline: ${modelName}`,
      newUrl
    );
    
    console.log('✓ URL updated to:', newUrl);
  };

  // Metoda 1: Nasłuchuj kliknięcia na elementy modelu
  const attachClickListeners = () => {
    document.addEventListener('click', (e) => {
      // Szukaj najbliższego elementu z data-model lub tekst zawierający model
      let target = e.target.closest('[data-model], [data-value]');
      
      if (target) {
        const modelName = target.getAttribute('data-model') || 
                         target.getAttribute('data-value') || 
                         target.textContent?.trim();
        
        if (modelName && modelName.length > 0) {
          updateUrlWithModel(modelName);
        }
      }
    }, true);
  };

  // Metoda 2: Obserwuj zmiany w elementach zawierających nazwę modelu
  const observeModelDisplay = () => {
    const observer = new MutationObserver(() => {
      // Szukaj elementu pokazującego wybrany model
      const modelElements = [
        document.querySelector('button[class*="model"]'),
        document.querySelector('[class*="selected"] [class*="model"]'),
        document.querySelector('[class*="current-model"]'),
      ].filter(Boolean);

      for (const el of modelElements) {
        const modelName = el?.textContent?.trim();
        if (modelName) {
          updateUrlWithModel(modelName);
        }
      }
    });

    const config = {
      subtree: true,
      childList: true,
      characterData: true,
      attributes: true,
    };

    const targetElement = document.querySelector('main') || document.body;
    if (targetElement) {
      observer.observe(targetElement, config);
    }
  };

  // Metoda 3: Przesłuchuj zdarzenia localStorage
  const observeLocalStorage = () => {
    const originalSetItem = Storage.prototype.setItem;
    
    Storage.prototype.setItem = function(key, value) {
      originalSetItem.apply(this, arguments);
      
      if (key.includes('model') || key.includes('selectedModel')) {
        try {
          const parsed = typeof value === 'string' ? JSON.parse(value) : value;
          const modelName = parsed?.name || parsed?.id || parsed;
          
          if (modelName && typeof modelName === 'string') {
            updateUrlWithModel(modelName);
          }
        } catch (e) {
          // Może być zwykły string
          if (value && typeof value === 'string' && value.length < 100) {
            updateUrlWithModel(value);
          }
        }
      }
    };
  };

  // Metoda 4: Użyj Mutation Observer na całej stronie
  const globalObserver = () => {
    const observer = new MutationObserver(mutations => {
      mutations.forEach(mutation => {
        if (mutation.type === 'attributes' && mutation.target.textContent) {
          const text = mutation.target.textContent.trim();
          // Jeśli znaleźliśmy tekst zawierający "Mode" (jak "Safe Mode", "Smart Mode")
          if ((text.includes('Mode') || text.includes('mode')) && text.length < 100) {
            updateUrlWithModel(text);
          }
        }
      });
    });

    observer.observe(document.body, {
      attributes: true,
      subtree: true,
      attributeFilter: ['class', 'data-model', 'title', 'aria-label']
    });
  };

  // Wczytaj model z URL przy starcie
  const loadModelFromUrl = () => {
    const match = window.location.pathname.match(/\/index\/([^\/]+)/);
    if (match) {
      const modelName = decodeURIComponent(match[1]);
      lastModel = modelName;
      console.log('✓ Model z URL:', modelName);
    }
  };

  // Inicjalizacja
  const init = () => {
    loadModelFromUrl();
    attachClickListeners();
    observeModelDisplay();
    observeLocalStorage();
    globalObserver();
    
    console.log('✓ Pipeline Routing initialized successfully');
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Dodatkowa inicjalizacja po 2s (w razie gdy strona się leniwale ładuje)
  setTimeout(init, 2000);
})();
