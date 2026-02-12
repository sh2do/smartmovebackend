# Sign-In HTTP Error Fix - TODO

## Problem

Backend returns `{"status": "success", "data": {"token": ..., "user": ...}}` but frontend tries to extract `token` and `user` directly from response.

## Fix Plan

1. Update `smartmovefrontend/smartmove/src/utils/api.js` to unwrap `data` property from standard backend response
2. This will fix sign-in and all other API calls automatically

## Status

- [x] Update api.js to handle wrapped response format
