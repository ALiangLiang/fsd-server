var Position = require('./messages/Position')

module.exports = {}

module.exports.fixRadialDistance = function fixRadialDistance(position, bearing, distance) {
  const { latitude, longitude } = position
  // Vincenty's formulae constants
  const a = 6378137; // 赤道半徑 (m)
  const f = 1 / 298.257223563; // 扁率
  const pi = Math.PI;

  // 將角度轉換為弧度
  const toRadians = function (degrees) {
    return degrees * pi / 180;
  };

  // 將弧度轉換為角度
  const toDegrees = function (radians) {
    return radians * 180 / pi;
  };

  // 計算目標點的緯度與經度
  const calculateDestinationPoint = function (lat1, lon1, initialBearing, distance) {
    const φ1 = toRadians(lat1);
    const λ1 = toRadians(lon1);
    const α1 = toRadians(initialBearing);
    const s = distance;

    const sinφ1 = Math.sin(φ1);
    const cosφ1 = Math.cos(φ1);
    const tanφ1 = Math.tan(φ1);

    const α = Math.atan2(Math.sin(α1) * Math.sin(s / a) * cosφ1,
      Math.cos(s / a) - sinφ1 * sinφ1);

    const δ = Math.atan2(sinφ1 * Math.sin(s / a) * Math.cos(α1),
      Math.cos(s / a) - sinφ1 * Math.cos(α1));

    const x = δ * Math.sin(α);
    const y = Math.log(Math.tan(pi / 4 + φ1 / 2) * Math.pow((1 - f * sinφ1) / (1 + f * sinφ1), f / 2));

    const sinφ2 = sinφ1 * Math.cos(s / a) + cosφ1 * Math.sin(s / a) * Math.cos(α1);
    const φ2 = Math.atan2(sinφ2, Math.sqrt(1 - sinφ2 * sinφ2));

    const λ = λ1 + Math.atan2(Math.sin(s / a) * Math.sin(α1),
      Math.cos(s / a) - sinφ1 * Math.cos(α1));

    const destinationLatitude = toDegrees(φ2);
    const destinationLongitude = toDegrees(λ);

    return new Position(destinationLatitude, destinationLongitude)
  };

  const destinationPoint = calculateDestinationPoint(latitude, longitude, bearing, distance);

  return destinationPoint;
}