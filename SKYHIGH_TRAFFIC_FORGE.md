# Skyhigh Traffic Forge 🚀

**Web Gateway Traffic Simulator for CASB Demonstrations**

## New Branding Applied ✅

The project has been successfully rebranded from "Shadow IT Generator" to **"Skyhigh Traffic Forge"**:

### Updated Components:

1. **Docker Image & Container**
   - Image name: `skyhigh-traffic-forge`
   - User: `skyhigh`
   - Config path: `/etc/skyhigh-traffic-forge`
   - Log path: `/var/log/skyhigh-traffic-forge`

2. **Command Line**
   - Command: `skyhigh-traffic-forge`
   - Package name: `skyhigh-traffic-forge`

3. **Documentation**
   - README.md updated with new branding
   - All examples use new command names
   - Positioned as "CASB demo system"

4. **Docker Labels**
   ```dockerfile
   LABEL maintainer="Skyhigh Security"
   LABEL description="Skyhigh Traffic Forge - Web Gateway Traffic Simulator for CASB Demos"
   ```

## Quick Start with New Name

```bash
# Build the image
docker build -t skyhigh-traffic-forge .

# Initialize configuration
docker run -v ~/config:/etc/skyhigh-traffic-forge \
  skyhigh-traffic-forge init

# Generate traffic
docker run -v ~/config:/etc/skyhigh-traffic-forge \
  -v ~/logs:/var/log/skyhigh-traffic-forge \
  skyhigh-traffic-forge generate --mode realtime
```

## Why "Traffic Forge"?

- **Professional** - Sounds enterprise-grade
- **Descriptive** - "Forge" implies crafting/creating traffic
- **Brand-aligned** - Includes "Skyhigh" name
- **Memorable** - Strong, distinctive name

## Marketing Benefits

1. **No "Shadow IT" stigma** - Positive connotations only
2. **Clear purpose** - Traffic generation for testing
3. **Enterprise appeal** - Sounds like a professional tool
4. **CASB focus** - Aligned with Skyhigh Security's market

## Internal Package Note

The internal Python package is still named `shadow_it_generator` to avoid massive refactoring, but all external-facing components use the new "Skyhigh Traffic Forge" branding.

## Ready for Skyhigh Security! 🎯

The tool is now properly branded for Skyhigh Security's CASB demo system, with a professional name that emphasizes its purpose as a traffic simulation tool rather than focusing on "shadow IT" which might have negative connotations.