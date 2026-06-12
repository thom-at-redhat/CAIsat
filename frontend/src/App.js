import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import * as THREE from 'three';
import { MapContainer, TileLayer, useMapEvents, Rectangle } from 'react-leaflet';
import leafletImage from 'leaflet-image';
import 'leaflet/dist/leaflet.css';
import './App.css';

function App() {
  const [view, setView] = useState('globe'); // 'globe', 'map', or 'processing'
  const [enhancementCount, setEnhancementCount] = useState(0);
  const [systemOnline, setSystemOnline] = useState(false);
  const [captureMode, setCaptureMode] = useState(false);
  const [selectedArea, setSelectedArea] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [enhancedImage, setEnhancedImage] = useState(null);
  const [processing, setProcessing] = useState(false);
  const globeRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const earthRef = useRef(null);
  const mapRef = useRef(null);

  // API endpoint
  const BACKEND_BASE = window.location.hostname.includes('localhost')
    ? 'http://localhost:8080'
    : `${window.location.protocol}//${window.location.hostname.replace('caisat', 'caisat-backend')}`;

  // Check system health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await axios.get(`${BACKEND_BASE}/health`, { timeout: 5000 });
        setSystemOnline(true);
      } catch (err) {
        setSystemOnline(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [BACKEND_BASE]);

  // Fetch enhancement stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${BACKEND_BASE}/api/stats`);
        setEnhancementCount(response.data.total_enhancements);
      } catch (error) {
        console.log('Stats not available');
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, [BACKEND_BASE]);

  // Initialize Three.js globe
  useEffect(() => {
    if (!globeRef.current || view !== 'globe') return;

    const container = globeRef.current;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 100000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // Earth
    const earthGeometry = new THREE.SphereGeometry(6371, 64, 64);
    const textureLoader = new THREE.TextureLoader();
    const earthMaterial = new THREE.MeshPhongMaterial({
      map: textureLoader.load('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg'),
      bumpMap: textureLoader.load('https://unpkg.com/three-globe/example/img/earth-topology.png'),
      bumpScale: 10
    });
    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
    scene.add(earth);

    // Atmosphere
    const atmosphereGeometry = new THREE.SphereGeometry(6471, 64, 64);
    const atmosphereMaterial = new THREE.MeshBasicMaterial({
      color: 0x4488ff,
      transparent: true,
      opacity: 0.1,
      side: THREE.BackSide
    });
    const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    scene.add(atmosphere);

    // Lights
    const sunLight = new THREE.DirectionalLight(0xffffff, 1);
    sunLight.position.set(5, 3, 5);
    scene.add(sunLight);
    scene.add(new THREE.AmbientLight(0x333333));

    camera.position.set(0, 0, 15000);

    sceneRef.current = scene;
    cameraRef.current = camera;
    rendererRef.current = renderer;
    earthRef.current = earth;

    // Animation loop
    function animate() {
      requestAnimationFrame(animate);
      earth.rotation.y += 0.0005; // West to East rotation
      renderer.render(scene, camera);
    }
    animate();

    // Cleanup
    return () => {
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [view]);

  const handleActivateSatelliteView = () => {
    setView('map');
  };

  const handleCaptureEnhance = () => {
    setCaptureMode(true);
  };

  const handleAreaSelect = async (bounds) => {
    if (!mapRef.current) return;

    setSelectedArea(bounds);
    setCaptureMode(false);

    // Capture the map as an image
    try {
      const map = mapRef.current;

      leafletImage(map, async (err, canvas) => {
        if (err) {
          console.error('Error capturing map:', err);
          alert('Error capturing map view');
          return;
        }

        // Convert canvas to blob
        canvas.toBlob(async (blob) => {
          // Create FormData
          const formData = new FormData();
          formData.append('image', blob, 'capture.png');

          // Show captured image
          const imageUrl = URL.createObjectURL(blob);
          setCapturedImage(imageUrl);
          setView('processing');
          setProcessing(true);

          try {
            // Send to backend for enhancement
            const response = await axios.post(`${BACKEND_BASE}/api/enhance`, formData, {
              headers: { 'Content-Type': 'multipart/form-data' },
              responseType: 'blob'
            });

            // Create URL for enhanced image
            const enhancedUrl = URL.createObjectURL(response.data);
            setEnhancedImage(enhancedUrl);
            setProcessing(false);
          } catch (error) {
            console.error('Enhancement failed:', error);
            alert('Enhancement failed: ' + error.message);
            setProcessing(false);
          }
        }, 'image/png');
      });
    } catch (error) {
      console.error('Capture error:', error);
      alert('Error: ' + error.message);
    }
  };

  // Map selection component
  function MapSelector() {
    const [startPos, setStartPos] = useState(null);
    const [currentPos, setCurrentPos] = useState(null);

    useMapEvents({
      mousedown: (e) => {
        if (captureMode) {
          setStartPos(e.latlng);
          setCurrentPos(e.latlng);
        }
      },
      mousemove: (e) => {
        if (captureMode && startPos) {
          setCurrentPos(e.latlng);
        }
      },
      mouseup: (e) => {
        if (captureMode && startPos) {
          const bounds = [
            [Math.min(startPos.lat, e.latlng.lat), Math.min(startPos.lng, e.latlng.lng)],
            [Math.max(startPos.lat, e.latlng.lat), Math.max(startPos.lng, e.latlng.lng)]
          ];
          handleAreaSelect(bounds);
          setStartPos(null);
          setCurrentPos(null);
        }
      }
    });

    if (captureMode && startPos && currentPos) {
      const bounds = [
        [Math.min(startPos.lat, currentPos.lat), Math.min(startPos.lng, currentPos.lng)],
        [Math.max(startPos.lat, currentPos.lat), Math.max(startPos.lng, currentPos.lng)]
      ];
      return <Rectangle bounds={bounds} pathOptions={{ color: '#ff4444', weight: 3 }} />;
    }

    return null;
  }

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <div className="header">
        <div className="logo">
          <span>CAIsat</span>
        </div>
        <div className="nav">
          <div className="nav-item active">Earth View</div>
          <div className="nav-item">Processing</div>
        </div>
        <div className="status">
          <div className={`status-dot ${systemOnline ? 'online' : ''}`}></div>
          {systemOnline ? 'LIVE' : 'OFFLINE'}
        </div>
      </div>

      {/* Main Container */}
      <div className="container">
        {/* Left Sidebar */}
        <div className="sidebar">
          <div className="section-header">● ENHANCEMENTS</div>
          <div className="section-title">Total Processed</div>
          <div className="section-count">{enhancementCount}</div>

          <div className="divider"></div>

          <div className="section-header">IMAGING SATELLITES</div>

          <div className="list-item">
            <div>
              <div className="item-title">Clarity-1</div>
              <div className="item-subtitle">CAIsat · AI-Enhanced Imaging</div>
            </div>
            <div className="item-badge">LIVE</div>
          </div>

          <div className="list-item">
            <div>
              <div className="item-title">Sentinel-2A</div>
              <div className="item-subtitle">ESA · Earth Observation</div>
            </div>
            <div className="item-badge">EOS</div>
          </div>

          <div className="list-item">
            <div>
              <div className="item-title">Landsat 8</div>
              <div className="item-subtitle">NASA/USGS · Imaging</div>
            </div>
            <div className="item-badge">IMG</div>
          </div>

          <div className="divider"></div>

          <div className="section-header">GROUND STATIONS</div>

          <div className="list-item">
            <div>
              <div className="item-title">CAIstellar Observatory</div>
              <div className="item-subtitle">Space Telescope · Deep Field</div>
            </div>
            <div className="item-badge">OBS</div>
          </div>
        </div>

        {/* Globe/Map Container */}
        <div className="globe">
          <div id="earthContainer">
            {/* 3D Globe */}
            {view === 'globe' && (
              <>
                <div ref={globeRef} className="globe3d"></div>
                <button className="activate-btn" onClick={handleActivateSatelliteView}>
                  Satellite View
                </button>
              </>
            )}

            {/* Leaflet Map */}
            {view === 'map' && (
              <>
                <MapContainer
                  ref={mapRef}
                  center={[37.7749, -122.4194]}
                  zoom={3}
                  minZoom={2}
                  maxZoom={19}
                  style={{ width: '100%', height: '100%', background: '#000', cursor: captureMode ? 'crosshair' : 'grab' }}
                  zoomControl={true}
                >
                  <TileLayer
                    attribution='Tiles &copy; Esri'
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    maxZoom={19}
                  />
                  <MapSelector />
                </MapContainer>
                {captureMode && (
                  <div style={{
                    position: 'fixed',
                    top: '60px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    background: 'rgba(255, 68, 68, 0.9)',
                    color: '#fff',
                    padding: '10px 20px',
                    borderRadius: '20px',
                    zIndex: 10000,
                    fontSize: '14px',
                    fontWeight: 700
                  }}>
                    Click and drag to select area to enhance
                  </div>
                )}
                {!captureMode && (
                  <button className="capture-btn" onClick={handleCaptureEnhance}>
                    Capture & Enhance
                  </button>
                )}
              </>
            )}

            {/* Processing View */}
            {view === 'processing' && (
              <div className="processing-view">
                <div className="processing-header">
                  <h2>Image Enhancement</h2>
                  <button className="back-btn" onClick={() => setView('map')}>← Back to Map</button>
                </div>
                <div className="processing-container">
                  <div className="image-panel">
                    <h3>Original Capture</h3>
                    {capturedImage && <img src={capturedImage} alt="Captured" />}
                  </div>
                  <div className="image-panel">
                    <h3>Enhanced Result</h3>
                    {processing ? (
                      <div className="loading">Processing with SwinIR...</div>
                    ) : enhancedImage ? (
                      <img src={enhancedImage} alt="Enhanced" />
                    ) : (
                      <div className="loading">Waiting...</div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
