const DATA = __I18N_JSON__;
const DEFAULT_LANG = "en";

const applyLang = (lang) => {
    for (const [id, translations] of Object.entries()) {
        elem = document.getElementById(id);
        if (elem) {
            let translation = "<ERROR>";
            try {
                translation = translations[lang] || translations[DEFAULT_LANG] || "<Missing translation>";
            } catch (e) {
                console.warn(e);
            }
            elem.innerHtml = translation;
        }
    }
}

const getLang = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get("lang") || DEFAULT_LANG;
}


let old_lang = "";

const updateLang = () => {
    const lang = getLang();
    if (lang !== old_lang) {
        old_lang = lang;
        applyLang(lang);
    }
}

// Repeatedly check url lang, and update elements if it changes
setInterval(updateLang, 100);