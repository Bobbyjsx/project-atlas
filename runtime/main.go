package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"strings"
)

const configEnv = "ATLAS_CONFIG"

func main() {
	if err := loadConfig(); err != nil {
		fatal(err)
	}

	args := os.Args[1:]
	if len(args) == 0 {
		fatal(fmt.Errorf("no application command provided"))
	}

	cmd := exec.Command(args[0], args[1:]...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Env = os.Environ()

	if err := cmd.Run(); err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			os.Exit(exitErr.ExitCode())
		}
		fatal(err)
	}
}

func loadConfig() error {
	raw, ok := os.LookupEnv(configEnv)
	if !ok || strings.TrimSpace(raw) == "" {
		return nil
	}

	var config map[string]any
	if err := json.Unmarshal([]byte(raw), &config); err != nil {
		return fmt.Errorf("invalid %s JSON: %w", configEnv, err)
	}

	for key, value := range config {
		if !validEnvName(key) {
			return fmt.Errorf("invalid environment variable name %q", key)
		}
		if key == configEnv {
			return fmt.Errorf("%s cannot contain itself", configEnv)
		}
		if value == nil {
			continue
		}
		text, ok := value.(string)
		if !ok {
			return fmt.Errorf("environment variable %q must be a string", key)
		}
		if err := os.Setenv(key, text); err != nil {
			return fmt.Errorf("set environment variable %q: %w", key, err)
		}
	}

	// Do not leave the aggregate secret in the application's environment.
	_ = os.Unsetenv(configEnv)
	return nil
}

func validEnvName(name string) bool {
	if name == "" {
		return false
	}
	for i, r := range name {
		if (r >= 'A' && r <= 'Z') || (r >= 'a' && r <= 'z') || r == '_' || (i > 0 && r >= '0' && r <= '9') {
			continue
		}
		return false
	}
	return true
}

func fatal(err error) {
	fmt.Fprintf(os.Stderr, "atlas-runtime: %v\n", err)
	os.Exit(1)
}
