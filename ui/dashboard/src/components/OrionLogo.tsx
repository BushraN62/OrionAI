import { motion } from 'framer-motion';

interface OrionLogoProps {
  size?: number;
  animated?: boolean;
}

export function OrionLogo({ size = 120, animated = true }: OrionLogoProps) {
  const strokeWidth = 1.5;
  const centerX = size / 2;
  const centerY = size / 2;
  const radius = size * 0.38; // Outer circle radius

  // Three belt circles positioned diagonally (top-left to bottom-right)
  const circleSize = size * 0.08;
  const spacing = size * 0.12;
  const beltCircles = [
    { cx: centerX - spacing, cy: centerY - spacing, r: circleSize },
    { cx: centerX, cy: centerY, r: circleSize },
    { cx: centerX + spacing, cy: centerY + spacing, r: circleSize },
  ];

  return (
    <motion.div
      initial={animated ? { opacity: 0, scale: 0.8 } : {}}
      animate={animated ? { opacity: 1, scale: 1 } : {}}
      transition={{ duration: 0.8, ease: 'easeOut' }}
      style={{ width: size, height: size }}
      className="relative flex items-center justify-center"
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="relative z-10"
      >
        {/* Main outer circle (light gray) */}
        <circle
          cx={centerX}
          cy={centerY}
          r={radius}
          fill="none"
          stroke="rgba(203, 213, 225, 0.4)"
          strokeWidth={strokeWidth}
        />

        {/* Top-right curved arc (purple/lavender gradient) */}
        <motion.path
          d={`M ${centerX + radius * Math.cos(-Math.PI / 6)}, ${centerY + radius * Math.sin(-Math.PI / 6)}
              A ${radius} ${radius} 0 0 1 ${centerX + radius * Math.cos(Math.PI / 6)}, ${centerY + radius * Math.sin(Math.PI / 6)}`}
          fill="none"
          stroke="url(#purpleGradient)"
          strokeWidth={strokeWidth + 0.5}
          strokeLinecap="round"
          initial={animated ? { pathLength: 0, opacity: 0 } : {}}
          animate={animated ? { pathLength: 1, opacity: 1 } : {}}
          transition={{ duration: 1.2, delay: 0.3, ease: 'easeInOut' }}
        />

        {/* Bottom-left curved arc (cyan/blue gradient) */}
        <motion.path
          d={`M ${centerX + radius * Math.cos(5 * Math.PI / 6)}, ${centerY + radius * Math.sin(5 * Math.PI / 6)}
              A ${radius} ${radius} 0 0 1 ${centerX + radius * Math.cos(7 * Math.PI / 6)}, ${centerY + radius * Math.sin(7 * Math.PI / 6)}`}
          fill="none"
          stroke="url(#cyanGradient)"
          strokeWidth={strokeWidth + 0.5}
          strokeLinecap="round"
          initial={animated ? { pathLength: 0, opacity: 0 } : {}}
          animate={animated ? { pathLength: 1, opacity: 1 } : {}}
          transition={{ duration: 1.2, delay: 0.5, ease: 'easeInOut' }}
        />

        {/* Three circles in diagonal line (Orion's belt) */}
        {beltCircles.map((circle, i) => (
          <motion.circle
            key={i}
            cx={circle.cx}
            cy={circle.cy}
            r={circle.r}
            fill="none"
            stroke="rgba(226, 232, 240, 0.8)"
            strokeWidth={strokeWidth}
            initial={animated ? { scale: 0, opacity: 0 } : {}}
            animate={animated ? { scale: 1, opacity: 1 } : {}}
            transition={{
              duration: 0.4,
              delay: 0.8 + i * 0.1,
              ease: 'easeOut',
            }}
            style={{ transformOrigin: `${circle.cx}px ${circle.cy}px` }}
          />
        ))}

        {/* Line connecting the three circles (Orion's belt line) */}
        <motion.line
          x1={beltCircles[0].cx}
          y1={beltCircles[0].cy}
          x2={beltCircles[2].cx}
          y2={beltCircles[2].cy}
          stroke="rgba(226, 232, 240, 0.6)"
          strokeWidth={strokeWidth * 0.8}
          strokeLinecap="round"
          initial={animated ? { pathLength: 0, opacity: 0 } : {}}
          animate={animated ? { pathLength: 1, opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 1.1, ease: 'easeOut' }}
        />

        {/* Small sparkle stars at arc endpoints */}
        <motion.g
          initial={animated ? { opacity: 0, scale: 0 } : {}}
          animate={animated ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.3, delay: 1.5 }}
        >
          {/* Top-right sparkle (purple) */}
          <g transform={`translate(${centerX + radius * Math.cos(Math.PI / 6)}, ${centerY + radius * Math.sin(Math.PI / 6)})`}>
            <circle r="2.5" fill="#b4a7d6" opacity="0.9" />
            <circle r="1" fill="#e8e2f7" />
          </g>
          
          {/* Bottom-left sparkle (cyan) */}
          <g transform={`translate(${centerX + radius * Math.cos(7 * Math.PI / 6)}, ${centerY + radius * Math.sin(7 * Math.PI / 6)})`}>
            <circle r="2.5" fill="#7dd3e8" opacity="0.9" />
            <circle r="1" fill="#d4f1f9" />
          </g>
        </motion.g>

        {/* Gradients */}
        <defs>
          <linearGradient id="purpleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#b4a7d6" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#9b8cc4" stopOpacity="0.95" />
          </linearGradient>
          <linearGradient id="cyanGradient" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#7dd3e8" stopOpacity="0.95" />
            <stop offset="100%" stopColor="#5bc0d9" stopOpacity="0.85" />
          </linearGradient>
        </defs>
      </svg>

      {/* Subtle animated glow */}
      {animated && (
        <motion.div
          className="absolute inset-0 rounded-full pointer-events-none"
          style={{
            background: 'radial-gradient(circle, rgba(180,167,214,0.08) 0%, transparent 65%)',
          }}
          animate={{
            scale: [1, 1.15, 1],
            opacity: [0.2, 0.35, 0.2],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      )}
    </motion.div>
  );
}
