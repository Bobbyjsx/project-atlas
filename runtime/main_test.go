package main

import (
	"os"
	"testing"
)

func TestLoadConfigAbsentIsNoop(t *testing.T) {
	_ = os.Unsetenv(configEnv)
	_ = os.Unsetenv("ATLAS_TEST_VALUE")

	if err := loadConfig(); err != nil {
		t.Fatal(err)
	}
}

func TestLoadConfigExportsStringValues(t *testing.T) {
	t.Setenv(configEnv, `{"ATLAS_TEST_VALUE":"hello","ATLAS_TEST_NUMBER":"123"}`)

	if err := loadConfig(); err != nil {
		t.Fatal(err)
	}

	if got := os.Getenv("ATLAS_TEST_VALUE"); got != "hello" {
		t.Fatalf("ATLAS_TEST_VALUE = %q, want hello", got)
	}
	if got := os.Getenv("ATLAS_TEST_NUMBER"); got != "123" {
		t.Fatalf("ATLAS_TEST_NUMBER = %q, want 123", got)
	}
	if _, ok := os.LookupEnv(configEnv); ok {
		t.Fatalf("%s should be removed before application startup", configEnv)
	}
}

func TestLoadConfigRejectsNonStringValues(t *testing.T) {
	t.Setenv(configEnv, `{"ATLAS_TEST_VALUE":123}`)
	if err := loadConfig(); err == nil {
		t.Fatal("expected non-string value to be rejected")
	}
}

func TestValidEnvName(t *testing.T) {
	for _, name := range []string{"PORT", "DATABASE_URL", "A1", "_PRIVATE"} {
		if !validEnvName(name) {
			t.Errorf("%q should be valid", name)
		}
	}
	for _, name := range []string{"", "1PORT", "PORT-NAME", "PORT.NAME"} {
		if validEnvName(name) {
			t.Errorf("%q should be invalid", name)
		}
	}
}
