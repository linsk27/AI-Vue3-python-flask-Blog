import hljs from 'highlight.js/lib/core'
import bash from 'highlight.js/lib/languages/bash'
import css from 'highlight.js/lib/languages/css'
import javascript from 'highlight.js/lib/languages/javascript'
import json from 'highlight.js/lib/languages/json'
import markdown from 'highlight.js/lib/languages/markdown'
import python from 'highlight.js/lib/languages/python'
import sql from 'highlight.js/lib/languages/sql'
import typescript from 'highlight.js/lib/languages/typescript'
import xml from 'highlight.js/lib/languages/xml'

let registered = false

export function getHighlight() {
    if (!registered) {
        hljs.registerLanguage('bash', bash)
        hljs.registerLanguage('css', css)
        hljs.registerLanguage('javascript', javascript)
        hljs.registerLanguage('js', javascript)
        hljs.registerLanguage('json', json)
        hljs.registerLanguage('markdown', markdown)
        hljs.registerLanguage('md', markdown)
        hljs.registerLanguage('python', python)
        hljs.registerLanguage('py', python)
        hljs.registerLanguage('sql', sql)
        hljs.registerLanguage('typescript', typescript)
        hljs.registerLanguage('ts', typescript)
        hljs.registerLanguage('xml', xml)
        hljs.registerLanguage('html', xml)
        registered = true
    }

    return hljs
}
