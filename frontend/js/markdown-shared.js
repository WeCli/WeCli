(function(global) {
    const ABSOLUTE_FILE_PATH_PATTERN = /(?:^|[\s(（\[{"'`])((?:\/[^\s<>"'`)\]）}]+)+\.[A-Za-z0-9_-]+(?::\d+(?::\d+)?)?)/g;
    const LOCAL_PREVIEW_ROUTE_PATTERN = /^\/local-file-(?:view|raw)(?:[/?#]|$)/;

    function parseLocalReference(rawValue) {
        const raw = String(rawValue || '').trim();
        if (!raw) return null;

        let candidate = raw;
        if (candidate.startsWith('file://')) {
            candidate = candidate.replace(/^file:\/\//i, '');
        }

        let hash = '';
        const hashIndex = candidate.indexOf('#');
        if (hashIndex >= 0) {
            hash = candidate.slice(hashIndex + 1);
            candidate = candidate.slice(0, hashIndex);
        }

        const lineColMatch = candidate.match(/^(.*?):(\d+)(?::(\d+))?$/);
        let path = candidate;
        let line = '';
        let col = '';
        if (lineColMatch) {
            path = lineColMatch[1];
            line = lineColMatch[2] || '';
            col = lineColMatch[3] || '';
        }

        if (!path) return null;
        const normalizedPath = path.replace(/\\/g, '/');
        if (/^[a-z][a-z0-9+.-]*:/i.test(normalizedPath) && !/^file:/i.test(normalizedPath)) {
            return null;
        }
        const looksAbsolute = normalizedPath.startsWith('/') || /^[A-Za-z]:\//.test(normalizedPath);
        const looksRelativeFile = /^[A-Za-z0-9._-]/.test(normalizedPath) && /[/.]/.test(normalizedPath);
        if (!looksAbsolute && !looksRelativeFile) return null;

        if (hash && !line) {
            const hashMatch = hash.match(/^L(\d+)(?:C(\d+))?$/i);
            if (hashMatch) {
                line = hashMatch[1] || '';
                col = hashMatch[2] || '';
            }
        }

        return { path, line, col };
    }

    function buildLocalFilePreviewUrl(rawValue) {
        const raw = String(rawValue || '').trim();
        if (!raw || LOCAL_PREVIEW_ROUTE_PATTERN.test(raw)) return null;
        const parsed = parseLocalReference(rawValue);
        if (!parsed) return null;
        const params = new URLSearchParams();
        params.set('path', parsed.path);
        if (parsed.line) params.set('line', parsed.line);
        if (parsed.col) params.set('col', parsed.col);
        return `/local-file-view?${params.toString()}`;
    }

    function rewriteLocalFileLinks(root) {
        if (!root) return;
        root.querySelectorAll('a[href]').forEach((anchor) => {
            if (anchor.dataset.localFileLink === '1') return;
            const rawHref = anchor.getAttribute('href') || '';
            if (LOCAL_PREVIEW_ROUTE_PATTERN.test(rawHref)) {
                anchor.dataset.localFileLink = '1';
                anchor.classList.add('cc-local-file-link');
                return;
            }
            const previewUrl = buildLocalFilePreviewUrl(rawHref);
            if (!previewUrl) return;
            anchor.setAttribute('href', previewUrl);
            anchor.setAttribute('target', '_blank');
            anchor.setAttribute('rel', 'noopener noreferrer');
            anchor.dataset.localFileLink = '1';
            anchor.classList.add('cc-local-file-link');
        });
    }

    function linkifyLocalFileText(root) {
        if (!root || typeof document === 'undefined') return;
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
            acceptNode(node) {
                const parent = node && node.parentElement;
                if (!parent) return NodeFilter.FILTER_REJECT;
                if (parent.closest('a, code, pre, script, style, textarea')) {
                    return NodeFilter.FILTER_REJECT;
                }
                const text = String(node.nodeValue || '');
                ABSOLUTE_FILE_PATH_PATTERN.lastIndex = 0;
                return ABSOLUTE_FILE_PATH_PATTERN.test(text)
                    ? NodeFilter.FILTER_ACCEPT
                    : NodeFilter.FILTER_REJECT;
            }
        });

        const textNodes = [];
        let current = walker.nextNode();
        while (current) {
            textNodes.push(current);
            current = walker.nextNode();
        }

        textNodes.forEach((node) => {
            const text = String(node.nodeValue || '');
            ABSOLUTE_FILE_PATH_PATTERN.lastIndex = 0;
            let match;
            let lastIndex = 0;
            let replaced = false;
            const fragment = document.createDocumentFragment();

            while ((match = ABSOLUTE_FILE_PATH_PATTERN.exec(text)) !== null) {
                const fullMatch = match[0];
                const pathText = match[1];
                const leadLength = fullMatch.length - pathText.length;
                const matchStart = match.index + leadLength;

                if (matchStart > lastIndex) {
                    fragment.appendChild(document.createTextNode(text.slice(lastIndex, matchStart)));
                }

                const previewUrl = buildLocalFilePreviewUrl(pathText);
                if (previewUrl) {
                    const anchor = document.createElement('a');
                    anchor.href = previewUrl;
                    anchor.target = '_blank';
                    anchor.rel = 'noopener noreferrer';
                    anchor.dataset.localFileLink = '1';
                    anchor.className = 'cc-local-file-link';
                    anchor.textContent = pathText;
                    fragment.appendChild(anchor);
                    replaced = true;
                } else {
                    fragment.appendChild(document.createTextNode(pathText));
                }

                lastIndex = matchStart + pathText.length;
            }

            if (!replaced) return;
            if (lastIndex < text.length) {
                fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
            }
            node.parentNode.replaceChild(fragment, node);
        });
    }

    function escapeHtml(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    /**
     * API / LLM 有时把换行打成字面量反斜杠+n（两个字符），界面会原样显示「\n」。
     * 在 Markdown 或纯文本展示前转成真实换行（不处理已含真实换行的正常字符串）。
     */
    function normalizeEscapedNewlines(s) {
        const str = s == null ? '' : String(s);
        if (str.indexOf('\\') === -1) return str;
        return str
            .replace(/\\r\\n/g, '\n')
            .replace(/\\n/g, '\n')
            .replace(/\\r/g, '\n')
            .replace(/\\t/g, '\t');
    }

    function configureMarked() {
        if (typeof global.marked === 'undefined') return;
        if (global.marked.__clawcrossConfigured) return;

        global.marked.setOptions({
            gfm: true,
            // LLM 常用「单行换行」分段；开启后单 \n 转为 <br>，移动端可读性更好
            breaks: true,
            highlight(code, lang) {
                if (typeof global.hljs === 'undefined') {
                    return escapeHtml(code);
                }
                const language = lang && global.hljs.getLanguage(lang) ? lang : 'plaintext';
                return global.hljs.highlight(code, { language }).value;
            },
            langPrefix: 'hljs language-'
        });

        global.marked.__clawcrossConfigured = true;
    }

    function render(content) {
        const raw = normalizeEscapedNewlines(content == null ? '' : String(content));
        configureMarked();
        if (!raw) return '';
        if (typeof global.marked === 'undefined') {
            return escapeHtml(raw).replace(/\n/g, '<br>');
        }
        return global.marked.parse(raw);
    }

    function highlight(root) {
        linkifyLocalFileText(root);
        rewriteLocalFileLinks(root);
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

    global.ClawcrossMarkdown = {
        buildLocalFilePreviewUrl,
        configure: configureMarked,
        escapeHtml,
        linkifyLocalFileText,
        normalizeEscapedNewlines,
        parseLocalReference,
        render,
        highlight,
        renderInto,
        rewriteLocalFileLinks,
    };

    configureMarked();
})(window);
