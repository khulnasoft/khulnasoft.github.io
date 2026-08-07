<?php
// KhulnaSoft Engineering Knowledge OS SDK (generated). Do not hand-edit.

final class AecClient
{
    private const BASE = 'https://khulnasoft.github.io/api';

    public static function resources(): string
    {
        return self::BASE . '/resources';
    }

    public static function resource(string $slug): string
    {
        return self::BASE . str_replace('{slug}', $slug, '/resources/{slug}');
    }

    public static function twin(string $slug): string
    {
        return self::BASE . str_replace('{slug}', $slug, '/resources/{slug}/twin');
    }

    public static function context(string $slug): string
    {
        return self::BASE . str_replace('{slug}', $slug, '/resources/{slug}/context');
    }

    public static function recommendations(string $slug): string
    {
        return self::BASE . str_replace('{slug}', $slug, '/resources/{slug}/recommendations');
    }

    public static function graph(): string
    {
        return self::BASE . '/graph';
    }

    public static function impact(): string
    {
        return self::BASE . '/impact';
    }

    public static function events(): string
    {
        return self::BASE . '/events';
    }

    public static function analytics(): string
    {
        return self::BASE . '/analytics';
    }

    public static function release(): string
    {
        return self::BASE . '/release';
    }

}
