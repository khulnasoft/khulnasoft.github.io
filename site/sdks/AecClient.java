// KhulnaSoft Engineering Knowledge OS SDK (generated). Do not hand-edit.
package io.khulnasoft;

public final class AecClient {
    private static final String BASE = "https://khulnasoft.github.io/api";

    public static String resources() {
        return BASE + "/resources";
    }

    public static String resource(String slug) {
        return BASE + "/resources/{slug}".replace("{slug}", slug);
    }

    public static String twin(String slug) {
        return BASE + "/resources/{slug}/twin".replace("{slug}", slug);
    }

    public static String context(String slug) {
        return BASE + "/resources/{slug}/context".replace("{slug}", slug);
    }

    public static String recommendations(String slug) {
        return BASE + "/resources/{slug}/recommendations".replace("{slug}", slug);
    }

    public static String graph() {
        return BASE + "/graph";
    }

    public static String impact() {
        return BASE + "/impact";
    }

    public static String events() {
        return BASE + "/events";
    }

    public static String analytics() {
        return BASE + "/analytics";
    }

    public static String release() {
        return BASE + "/release";
    }

}
