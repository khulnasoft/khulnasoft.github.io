// KhulnaSoft Engineering Knowledge OS SDK (generated). Do not hand-edit.

class AecClient {
  static const String base = "https://khulnasoft.github.io/api";

  static String resources() => base + "/resources";

  static String resource(String slug) {
    return base + "/resources/{slug}".replaceAll("{slug}", slug);
  }

  static String twin(String slug) {
    return base + "/resources/{slug}/twin".replaceAll("{slug}", slug);
  }

  static String context(String slug) {
    return base + "/resources/{slug}/context".replaceAll("{slug}", slug);
  }

  static String recommendations(String slug) {
    return base + "/resources/{slug}/recommendations".replaceAll("{slug}", slug);
  }

  static String graph() => base + "/graph";

  static String impact() => base + "/impact";

  static String events() => base + "/events";

  static String analytics() => base + "/analytics";

  static String release() => base + "/release";

}
