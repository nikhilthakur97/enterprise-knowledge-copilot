// Tiny inline-markdown renderer.
//
// The Gemini answer occasionally includes **bold**, *italic*, and `code`
// from its system-prompt-following behaviour. Rendering them as literal
// asterisks looks unfinished. A real markdown library would be overkill
// for ~3 inline patterns, so this is a safe hand-rolled renderer:
// returns an array of React nodes, no dangerouslySetInnerHTML, so React's
// auto-escaping prevents any HTML injection from model output.
//
// Block-level structure (newlines, lists) is preserved by the parent's
// `white-space: pre-wrap`, so we only need inline handling here.

import type { ReactNode } from 'react';

const PATTERN = /(`[^`]+`)|(\*\*[^*]+\*\*)|(\*[^*]+\*)/g;

export function renderMarkdown(text: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  let lastIndex = 0;
  let key = 0;
  let match: RegExpExecArray | null;

  while ((match = PATTERN.exec(text)) !== null) {
    if (match.index > lastIndex) {
      nodes.push(text.slice(lastIndex, match.index));
    }
    const [whole] = match;
    if (whole.startsWith('**')) {
      nodes.push(<strong key={key++}>{whole.slice(2, -2)}</strong>);
    } else if (whole.startsWith('*')) {
      nodes.push(<em key={key++}>{whole.slice(1, -1)}</em>);
    } else if (whole.startsWith('`')) {
      nodes.push(<code key={key++}>{whole.slice(1, -1)}</code>);
    }
    lastIndex = match.index + whole.length;
  }
  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }
  return nodes;
}
