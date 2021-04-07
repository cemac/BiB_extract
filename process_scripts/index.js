// d.ellis 2020
var width = window.innerWidth,
    height = window.innerHeight;
var sphere;
var run = true;

var freq = document.getElementById('freq')
var dt = document.getElementById('dt')


var renderer = new THREE.WebGLRenderer({ width: width,height:height, antialias: true });
renderer.setClearColor(new THREE.Color("#222"));
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.z = 5;


const audioContext = new (window.AudioContext || window.webkitAudioContext)();
analyser = audioContext.createAnalyser();
analyser.fftSize = 2 ** 14;
analyser.frequencyBinCount = 2 ** 14;
var f = Math.floor(analyser.frequencyBinCount ** 0.5);
if (!sphere) {
  makesphere(f, f);
  polar = sphere.geometry.vertices.map(d => c2p(d));
  renderer.render(scene, camera);
}

const gain = audioContext.createGain();
gain.gain.value = 0.01;
gain.connect(audioContext.destination);
gain.connect(analyser);

const oscillator = audioContext.createOscillator();
oscillator.type = "sine";
oscillator.start();
oscillator.connect(gain);

const waveform = new Float32Array(analyser.frequencyBinCount);

function updateWaveform() {
  analyser.getFloatTimeDomainData(waveform);
  if (run) {
    update(waveform);
    requestAnimationFrame(updateWaveform);
  }
}

requestAnimationFrame(updateWaveform);

document.body.addEventListener(
  "mousemove",
  function(event) {
    var pageX = event.pageX / width;
    var pageY = event.pageY / height;

    var f = (0.35 + pageY) * 3000
    oscillator.frequency.setValueAtTime(
      f,
      audioContext.currentTime
    );


    freq.textContent=Math.ceil(f)
    var d = -100 + pageX * 200;
    audioContext.detune = d
    dt.textContent=Math.ceil(d)
  },
  false
);

function update() {
  sphere.geometry.vertices = [...waveform]
    .slice(0, polar.length)
    .map((c, i) => {
      return p2c(polar[i], 1 + 2.5 * c);
    });

  // sphere.geometry.vertices=v
  camera.updateProjectionMatrix();
  sphere.geometry.computeVertexNormals();

  var geometry = sphere.geometry;
  geometry.verticesNeedUpdate = true;
  geometry.elementsNeedUpdate = true;
  geometry.morphTargetsNeedUpdate = true;
  geometry.uvsNeedUpdate = true;
  geometry.normalsNeedUpdate = true;
  geometry.colorsNeedUpdate = true;
  geometry.tangentsNeedUpdate = true;
  // camera.lookAt(scene.position);
  renderer.render(scene, camera);
}


function makesphere(x, y) {
  var sphere_geometry = new THREE.SphereGeometry(1, x, y);
  var material = new THREE.MeshNormalMaterial();
  sphere = new THREE.Mesh(sphere_geometry, material);
  scene.add(sphere);
}




function p2c(i, radius) {
  // console.log(i)
  var phi = i[0];
  var theta = i[1];
  return  new THREE.Vector3(
    radius * Math.sin(phi) * Math.sin(theta) || 0,
    radius * Math.cos(phi) || 0,
    radius * Math.sin(phi) * Math.cos(theta) || 0
  );

}

function c2p(coord, radius) {
  var theta = Math.atan2(coord.x, -coord.z);
  //  var length = Math.sqrt( coord.x * coord.x + coord.z * coord.z )
  var phi = Math.acos(coord.y);
  return [phi, theta];
}



window.onresize = resize;

function resize() {
  var aspect = window.innerWidth / window.innerHeight;
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = aspect;
  camera.updateProjectionMatrix();
  //controls.handleResize();
}
