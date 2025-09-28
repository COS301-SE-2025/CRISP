import { useRef, useEffect } from 'react';

const RippleGrid = ({
  className = '',
  enableRainbow = false,
  gridColor = '#ffffff',
  rippleIntensity = 0.05,
  gridSize = 10.0,
  gridThickness = 15.0,
  fadeDistance = 1.5,
  vignetteStrength = 2.0,
  glowIntensity = 0.1,
  opacity = 1.0,
  gridRotation = 0,
  mouseInteraction = false,
  mouseInteractionRadius = 0.8
}) => {
  const mountRef = useRef();

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    let animationFrameId;
    let time = 0;

    const vMouse = { x: 0.5, y: 0.5 };
    const vMouseDamp = { x: 0.5, y: 0.5 };
    let w = 1, h = 1;

    // Create canvas with explicit styles to ensure visibility
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Force canvas styling to ensure it's visible
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '1';

    mount.appendChild(canvas);

    const resize = () => {
      if (!mountRef.current) return;
      const container = mountRef.current;
      w = container.clientWidth || 400;
      h = container.clientHeight || 400;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);

      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + 'px';
      canvas.style.height = h + 'px';
      ctx.scale(dpr, dpr);
    };

    const onPointerMove = e => {
      if (!mouseInteraction || !mount) return;
      const rect = mount.getBoundingClientRect();
      vMouse.x = (e.clientX - rect.left) / w;
      vMouse.y = (e.clientY - rect.top) / h;
    };

    const drawGrid = () => {
      if (!ctx || w <= 0 || h <= 0) return;

      ctx.clearRect(0, 0, w, h);

      // Apply rotation
      ctx.save();
      ctx.translate(w / 2, h / 2);
      ctx.rotate((gridRotation * Math.PI) / 180);
      ctx.translate(-w / 2, -h / 2);

      // Grid parameters
      const centerX = w / 2;
      const centerY = h / 2;
      const spacing = Math.max(gridSize, 5); // Ensure minimum spacing
      const thickness = Math.max(gridThickness / 10, 0.5); // Ensure minimum thickness

      // Parse grid color
      let color;
      if (enableRainbow) {
        const hue = (time * 50) % 360;
        color = `hsla(${hue}, 70%, 60%, ${opacity})`;
      } else {
        // Parse hex color or use default
        let r = 255, g = 255, b = 255;
        if (gridColor.startsWith('#') && gridColor.length >= 7) {
          r = parseInt(gridColor.slice(1, 3), 16) || 255;
          g = parseInt(gridColor.slice(3, 5), 16) || 255;
          b = parseInt(gridColor.slice(5, 7), 16) || 255;
        }
        color = `rgba(${r}, ${g}, ${b}, ${opacity})`;
      }

      ctx.strokeStyle = color;
      ctx.lineWidth = thickness;

      // Draw vertical lines
      for (let x = 0; x <= w; x += spacing) {
        const distFromCenter = Math.abs(x - centerX) / centerX;
        const rippleEffect = mouseInteraction ?
          Math.sin(time * 3 + Math.abs(x - vMouseDamp.x * w) * 0.02) * rippleIntensity * 50 :
          Math.sin(time * 2 + x * 0.01) * rippleIntensity * 20;

        const fade = Math.max(0, 1 - (distFromCenter / fadeDistance));
        const vignette = Math.max(0, 1 - Math.pow(distFromCenter, vignetteStrength));

        ctx.globalAlpha = fade * vignette * opacity;

        ctx.beginPath();
        ctx.moveTo(x + rippleEffect, 0);
        ctx.lineTo(x + rippleEffect, h);
        ctx.stroke();
      }

      // Draw horizontal lines
      for (let y = 0; y <= h; y += spacing) {
        const distFromCenter = Math.abs(y - centerY) / centerY;
        const rippleEffect = mouseInteraction ?
          Math.sin(time * 3 + Math.abs(y - vMouseDamp.y * h) * 0.02) * rippleIntensity * 50 :
          Math.sin(time * 2 + y * 0.01) * rippleIntensity * 20;

        const fade = Math.max(0, 1 - (distFromCenter / fadeDistance));
        const vignette = Math.max(0, 1 - Math.pow(distFromCenter, vignetteStrength));

        ctx.globalAlpha = fade * vignette * opacity;

        ctx.beginPath();
        ctx.moveTo(0, y + rippleEffect);
        ctx.lineTo(w, y + rippleEffect);
        ctx.stroke();
      }

      // Add glow effect if enabled
      if (glowIntensity > 0) {
        ctx.globalCompositeOperation = 'screen';
        ctx.globalAlpha = glowIntensity;
        ctx.strokeStyle = color;
        ctx.lineWidth = thickness * 3;
        ctx.filter = 'blur(3px)';

        // Redraw subset with glow
        for (let x = 0; x <= w; x += spacing * 2) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, h);
          ctx.stroke();
        }
        for (let y = 0; y <= h; y += spacing * 2) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(w, y);
          ctx.stroke();
        }

        ctx.filter = 'none';
        ctx.globalCompositeOperation = 'source-over';
      }

      ctx.restore();
    };

    const update = () => {
      time = performance.now() * 0.001;

      // Smooth mouse movement
      if (mouseInteraction) {
        vMouseDamp.x += (vMouse.x - vMouseDamp.x) * 0.1;
        vMouseDamp.y += (vMouse.y - vMouseDamp.y) * 0.1;
      }

      drawGrid();
      animationFrameId = requestAnimationFrame(update);
    };

    // Initial setup
    setTimeout(() => {
      resize();
      update();
    }, 100);

    window.addEventListener('resize', resize);
    if (mouseInteraction) {
      document.addEventListener('mousemove', onPointerMove);
      document.addEventListener('pointermove', onPointerMove);
    }

    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
      window.removeEventListener('resize', resize);
      if (mouseInteraction) {
        document.removeEventListener('mousemove', onPointerMove);
        document.removeEventListener('pointermove', onPointerMove);
      }
      if (mount && canvas && mount.contains(canvas)) {
        mount.removeChild(canvas);
      }
    };
  }, [enableRainbow, gridColor, rippleIntensity, gridSize, gridThickness, fadeDistance, vignetteStrength, glowIntensity, opacity, gridRotation, mouseInteraction, mouseInteractionRadius]);

  return (
    <div
      className={className}
      ref={mountRef}
      style={{
        width: '100%',
        height: '100%',
        position: 'relative',
        overflow: 'hidden'
      }}
    />
  );
};

export default RippleGrid;