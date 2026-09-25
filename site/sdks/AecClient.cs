// KhulnaSoft Engineering Knowledge OS SDK (generated). Do not hand-edit.
namespace KhulnaSoft;

public static class AecClient
{
    private const string Base = "https://khulnasoft.github.io/api";

    public static string Resources() {
        return Base + "/resources";
    }

    public static string Resource(string slug) {
        return Base + "/resources/{slug}".Replace("{slug}", slug);
    }

    public static string Twin(string slug) {
        return Base + "/resources/{slug}/twin".Replace("{slug}", slug);
    }

    public static string Context(string slug) {
        return Base + "/resources/{slug}/context".Replace("{slug}", slug);
    }

    public static string Recommendations(string slug) {
        return Base + "/resources/{slug}/recommendations".Replace("{slug}", slug);
    }

    public static string Graph() {
        return Base + "/graph";
    }

    public static string Impact() {
        return Base + "/impact";
    }

    public static string Events() {
        return Base + "/events";
    }

    public static string Analytics() {
        return Base + "/analytics";
    }

    public static string Release() {
        return Base + "/release";
    }

}
