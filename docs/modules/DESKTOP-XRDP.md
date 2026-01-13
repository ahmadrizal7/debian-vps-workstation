# Desktop Module - XRDP Configuration

## Overview

The Desktop module configures a production-ready remote desktop environment using **XRDP with xorgxrdp backend** (Pure RDP - NO VNC) and XFCE4 desktop environment.

## Architecture

```
RDP Client → XRDP (port 3389) → xorgxrdp → Xorg → XFCE Desktop
(Pure RDP Protocol - No VNC Layer)
```

## Features

### ✅ Best Practice Configuration

Based on [neutrinolabs/xrdp](https://github.com/neutrinolabs/xrdp) official best practices:

1. **Pure XRDP/Xorg Backend**

   - NO VNC layer for better performance
   - Direct xorgxrdp module integration
   - Native Xorg rendering

2. **Performance Optimizations**

   - TCP optimizations (nodelay, keepalive)
   - Optimized buffers (32KB send, 64KB receive)
   - Bitmap caching and compression
   - Fast path enabled for input/output

3. **Dynamic Resolution Support**

   - Auto-adjusts to client screen size
   - Supports mobile portrait/landscape
   - Multi-monitor capable (up to 4 monitors)
   - Max resolution: 8192x8192

4. **XFCE Optimizations**

   - Compositor disabled for remote desktop
   - No visual effects over network
   - Screensaver and power management disabled
   - Optimized panel settings

5. **Security**
   - TLS 1.2/1.3 support
   - High encryption level
   - Credential requirements enforced
   - Proper file permissions

## Configuration

### Default Configuration

```yaml
desktop:
  enabled: true
  xrdp:
    max_bpp: 32
    bitmap_cache: true
    security_layer: "rdp"
    tcp_nodelay: true
  compositor:
    mode: "disabled"
```

### Files Generated

1. **`/etc/xrdp/xrdp.ini`**

   - Network optimizations
   - Bitmap caching and compression
   - Dynamic resolution support
   - Channel configurations
   - Xorg session definition

2. **`/etc/xrdp/sesman.ini`**

   - Session management
   - Xorg backend parameters
   - Logging configuration

3. **`/etc/X11/Xwrapper.config`**

   - Allows non-console users to start X server
   - Required for xrdp/xorgxrdp

4. **`~/.xsession` (per user)**
   - XFCE startup optimization
   - Compositor disabled
   - Screensaver disabled
   - dbus configuration

## Connection

### Linux

```bash
# Auto-resize with dynamic resolution
xfreerdp3 /v:SERVER_IP:3389 /u:username /p:password /cert:ignore /dynamic-resolution /smart-sizing

# Fullscreen with dynamic resolution
xfreerdp3 /v:SERVER_IP:3389 /u:username /p:password /cert:ignore /f /dynamic-resolution

# Mobile Portrait (1080x1920)
xfreerdp3 /v:SERVER_IP:3389 /u:username /p:password /cert:ignore /w:1080 /h:1920

# Mobile Landscape (1920x1080)
xfreerdp3 /v:SERVER_IP:3389 /u:username /p:password /cert:ignore /w:1920 /h:1080

# Using Remmina GUI
remmina
```

### Windows

1. Open Remote Desktop Connection (`Win+R`, type: `mstsc`)
2. Computer: `SERVER_IP`
3. Username: `your_username`
4. Click Connect

### macOS

1. Download Microsoft Remote Desktop from App Store
2. Add PC
3. PC name: `SERVER_IP`
4. User account: `username / password`
5. Connect

### Mobile

Use Microsoft Remote Desktop app or RD Client - resolution will auto-adjust to your device orientation.

## Troubleshooting

### X Server Failed to Start

**Symptom:** "Unable to open display :10" in logs

**Solution:** Check Xwrapper configuration

```bash
cat /etc/X11/Xwrapper.config
# Should contain:
# allowed_users=anybody
# needs_root_rights=yes
```

### Black Screen

**Symptom:** Connection succeeds but shows black screen

**Solution:**

1. Check .xsession file exists and is executable
2. Verify XFCE packages are installed
3. Check compositor is disabled

### Authentication Failed

**Symptom:** Invalid credentials error

**Solution:**

1. Verify user password: `sudo passwd username`
2. Check user is not system account (UID >= 1000)

### Portrait/Landscape Issues

**Symptom:** Display shows in wrong orientation on mobile

**Solution:** Use dynamic resolution flags:

```bash
xfreerdp3 /v:SERVER_IP /u:user /p:pass /cert:ignore /dynamic-resolution /smart-sizing
```

## Performance Tips

1. **For Mobile/Slow Connections:**

   - Use lower color depth: `/bpp:16`
   - Enable compression: Built-in with best practice config

2. **For LAN:**

   - Use full color: `/bpp:32` (default)
   - Enable all visual effects if desired

3. **For Multiple Monitors:**
   - Use `/multimon` flag
   - Configured to support up to 4 monitors

## Dependencies

- `xrdp` - RDP server
- `xorgxrdp` - Xorg backend for xrdp
- `xfce4` - Desktop environment
- `xfce4-goodies` - Additional XFCE utilities

## References

- [Official XRDP Project](https://github.com/neutrinolabs/xrdp)
- [XRDP Best Practices](https://github.com/neutrinolabs/xrdp/wiki)
- [Documentation](../XRDP-BEST-PRACTICE-APPLIED.md)

## Version

- **Last Updated:** 2026-01-10
- **Configuration:** Best Practice Applied
- **Backend:** Pure XRDP with xorgxrdp (NO VNC)
