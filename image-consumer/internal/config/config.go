package config

import (
	"log"
	"os"
)

var RTSPURL = getRequiredEnv("RTSP_URL")

const (
	OutputDir     = "/app/frames"
	MaxRetries    = 30
	RetryInterval = 1 // seconds
)

// getRequiredEnv retrieves an environment variable or panics if it's not set.
func getRequiredEnv(key string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	log.Fatalf("Error: Environment variable %s is not set.", key)
	return "" // Unreachable, but satisfies compiler
}
