// Package khulnasoft is a minimal client for the KhulnaSoft Engineering Knowledge OS.
// Generated. Do not hand-edit.
package khulnasoft

import (
	"fmt"
	"net/http"
	"strings"
)

const BaseURL = "https://khulnasoft.github.io/api"

type Client struct { HTTP *http.Client }

// resources returns the API payload.
func (c *Client) Resources() (*http.Response, error) {
	return c.HTTP.Get(BaseURL + "/resources")
}

// resource returns the resource identified by slug.
func (c *Client) Resource(slug string) (*http.Response, error) {
	return c.HTTP.Get(fmt.Sprintf("%s/resources/%s", BaseURL, slug))
}

// twin returns the resource identified by slug.
func (c *Client) Twin(slug string) (*http.Response, error) {
	return c.HTTP.Get(fmt.Sprintf("%s/resources/%s/twin", BaseURL, slug))
}

// context returns the resource identified by slug.
func (c *Client) Context(slug string) (*http.Response, error) {
	return c.HTTP.Get(fmt.Sprintf("%s/resources/%s/context", BaseURL, slug))
}

// recommendations returns the resource identified by slug.
func (c *Client) Recommendations(slug string) (*http.Response, error) {
	return c.HTTP.Get(fmt.Sprintf("%s/resources/%s/recommendations", BaseURL, slug))
}

// graph returns the API payload.
func (c *Client) Graph() (*http.Response, error) {
	return c.HTTP.Get(BaseURL + "/graph")
}

// impact returns the API payload.
func (c *Client) Impact() (*http.Response, error) {
	return c.HTTP.Get(BaseURL + "/impact")
}

// events returns the API payload.
func (c *Client) Events() (*http.Response, error) {
	return c.HTTP.Get(BaseURL + "/events")
}

// analytics returns the API payload.
func (c *Client) Analytics() (*http.Response, error) {
	return c.HTTP.Get(BaseURL + "/analytics")
}

// release returns the API payload.
func (c *Client) Release() (*http.Response, error) {
	return c.HTTP.Get(BaseURL + "/release")
}

// InstallAsset installs a reusable marketplace asset.
func (c *Client) InstallAsset(assetID string) (*http.Response, error) {
	req, _ := http.NewRequest("POST", BaseURL+"/marketplace/install", strings.NewReader(`{"id":"`+assetID+`"}`))
	req.Header.Set("Content-Type", "application/json")
	return c.HTTP.Do(req)
}

// ConsumeArtifact fetches the artifact resolved from an installed asset.
func (c *Client) ConsumeArtifact(assetID string) (*http.Response, error) {
	return c.HTTP.Get(BaseURL + "/marketplace?asset=" + assetID)
}

