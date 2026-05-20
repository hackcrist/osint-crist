<?php
// ============================================
// OSINT Bot - Tracker PHP
// ============================================
// Sube este archivo a la raíz de tu hosting
// ============================================

$secret = "osint2026";
$id = isset($_GET['c']) ? preg_replace('/[^a-zA-Z0-9_-]/', '', $_GET['c']) : 'default';
$is_fetch = isset($_GET['key']) && $_GET['key'] === $secret;

// Guardar logs afuera de public_html (mas seguro)
$log_dir = __DIR__ . '/../logs_tracker';
if (!is_dir($log_dir)) {
    @mkdir($log_dir, 0755, true);
}
$log_file = $log_dir . '/track_' . $id . '.json';

// Si viene con key secreta, devolver los logs como JSON
if ($is_fetch) {
    header('Content-Type: application/json');
    if (file_exists($log_file)) {
        echo file_get_contents($log_file);
    } else {
        echo json_encode([]);
    }
    exit;
}

// Registrar visita
$data = [
    'id'       => $id,
    'ip'       => $_SERVER['REMOTE_ADDR'] ?? '',
    'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? '',
    'referer'  => $_SERVER['HTTP_REFERER'] ?? '',
    'host'     => $_SERVER['HTTP_HOST'] ?? '',
    'uri'      => $_SERVER['REQUEST_URI'] ?? '',
    'time'     => date('Y-m-d H:i:s'),
    'language' => $_SERVER['HTTP_ACCEPT_LANGUAGE'] ?? '',
];

$logs = [];
if (file_exists($log_file)) {
    $logs = json_decode(file_get_contents($log_file), true) ?? [];
}
$logs[] = $data;

$max_logs = 100;
if (count($logs) > $max_logs) {
    $logs = array_slice($logs, -$max_logs);
}
file_put_contents($log_file, json_encode($logs, JSON_PRETTY_PRINT));

// Respuesta: 404 falsa
http_response_code(404);
header('Content-Type: text/html');
echo '<!DOCTYPE html><html><head><title>404</title></head><body><h1>404 Not Found</h1></body></html>';
exit;
