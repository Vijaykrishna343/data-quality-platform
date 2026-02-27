import { useCallback } from "react";
import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";

export default function ParticleBackground() {
  const particlesInit = useCallback(async (engine) => {
    await loadFull(engine);
  }, []);

  return (
    <Particles
      id="tsparticles"
      init={particlesInit}
      options={{
        background: { color: "transparent" },
        fpsLimit: 60,
        particles: {
          number: { value: 60 },
          color: { value: "#6366f1" },
          links: {
            enable: true,
            color: "#6366f1",
            distance: 150,
            opacity: 0.3,
          },
          move: { enable: true, speed: 1 },
          size: { value: 2 },
          opacity: { value: 0.4 },
        },
      }}
      className="absolute inset-0 -z-10"
    />
  );
}