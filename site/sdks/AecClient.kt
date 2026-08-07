// KhulnaSoft Engineering Knowledge OS SDK (generated). Do not hand-edit.

package io.khulnasoft

object AecClient {
    const val BASE = "https://khulnasoft.github.io/api"

    fun resources(): String = BASE + "/resources"

    fun resource(slug: String): String =
        BASE + "/resources/{slug}".replace("{slug}", slug)

    fun twin(slug: String): String =
        BASE + "/resources/{slug}/twin".replace("{slug}", slug)

    fun context(slug: String): String =
        BASE + "/resources/{slug}/context".replace("{slug}", slug)

    fun recommendations(slug: String): String =
        BASE + "/resources/{slug}/recommendations".replace("{slug}", slug)

    fun graph(): String = BASE + "/graph"

    fun impact(): String = BASE + "/impact"

    fun events(): String = BASE + "/events"

    fun analytics(): String = BASE + "/analytics"

    fun release(): String = BASE + "/release"

}
