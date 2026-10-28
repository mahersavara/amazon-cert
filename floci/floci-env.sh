# Point AWS CLI/SDK at Floci for the current shell only.
# Usage:  source floci/floci-env.sh
# Fake credentials on purpose: never put real AWS keys in this session.
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
unset AWS_PROFILE AWS_SESSION_TOKEN
echo "AWS CLI now targets Floci at $AWS_ENDPOINT_URL (this shell only)."
