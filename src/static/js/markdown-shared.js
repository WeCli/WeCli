(function(global) {
    function escapeHtml(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function configureMarked() {
        if (typeof global.marked === 'undefined') return;
        if (global.marked.__teamclawConfigured) return;

        global.marked.setOptions({
            highlight(code, lang) {
                if (typeof global.hljs === 'undefined') {
                    return escapeHtml(code);
                }
                const language = lang && global.hljs.getLanguage(lang) ? lang : 'plaintext';
                return global.hljs.highlight(code, { language }).value;
            },
            langPrefix: 'hljs language-'
        });

        global.marked.__teamclawConfigured = true;
    }

    function render(content) {
        const raw = content == null ? '' : String(content);
        configureMarked();
        if (!raw) return '';
        if (typeof global.marked === 'undefined') {
            return escapeHtml(raw).replace(/\n/g, '<br>');
        }
        return global.marked.parse(raw);
    }

    function highlight(root) {
        if (!root || typeof global.hljs === 'undefined') return;
        root.querySelectorAll('pre code').forEach((block) => {
            try {
                global.hljs.highlightElement(block);
            } catch (_) {
                // Ignore malformed snippets and keep rendering moving.
            }
        });
    }

    function renderInto(element, content) {
        if (!element) return;
        element.classList.add('markdown-body', 'tc-markdown');
        element.innerHTML = render(content);
        highlight(element);
    }

    global.TeamClawMarkdown = {
        configure: configureMarked,
        escapeHtml,
        render,
        highlight,
        renderInto,
    };

    configureMarked();
})(window);
