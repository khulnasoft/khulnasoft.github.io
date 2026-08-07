// KhulnaSoft Engineering Knowledge OS SDK (generated). Do not hand-edit.
export class AecClient {
  base = "https://khulnasoft.github.io/api";

  resources() = fetch(this.base + "/resources").then(r => r.json());
  resource(slug: string) = fetch(this.base + `/resources/${slug}`).then(r => r.json());
  twin(slug: string) = fetch(this.base + `/resources/${slug}/twin`).then(r => r.json());
  context(slug: string) = fetch(this.base + `/resources/${slug}/context`).then(r => r.json());
  recommendations(slug: string) = fetch(this.base + `/resources/${slug}/recommendations`).then(r => r.json());
  graph() = fetch(this.base + "/graph").then(r => r.json());
  impact() = fetch(this.base + "/impact").then(r => r.json());
  events() = fetch(this.base + "/events").then(r => r.json());
  analytics() = fetch(this.base + "/analytics").then(r => r.json());
  release() = fetch(this.base + "/release").then(r => r.json());
}
