// Citations panel: collapsible list of the chunks that grounded the answer.
//
// Uses native <details> / <summary> so the open/closed state lives in
// the browser rather than React state. Free keyboard + screen-reader
// support, and one fewer thing to test.

import type { Source } from '../types';

interface Props {
  sources: Source[];
}

export function Sources({ sources }: Props) {
  if (sources.length === 0) return null;

  return (
    <details className="sources">
      <summary>
        Sources <span className="sources-count">({sources.length})</span>
      </summary>
      <ol className="sources-list">
        {sources.map((s, i) => {
          const pct = Math.round(s.score * 100);
          return (
            <li key={i} className="source">
              <div className="source-header">
                <span className="source-file">{s.file}</span>
                {s.heading && (
                  <span className="source-heading"> :: {s.heading}</span>
                )}
                <span className="source-score">{pct}% match</span>
              </div>
              <pre className="source-snippet">{s.snippet}</pre>
            </li>
          );
        })}
      </ol>
    </details>
  );
}
