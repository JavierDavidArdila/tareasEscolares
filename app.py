from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime, date
import os

class TaskManagerHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        self.data_file = 'tasks.json'
        super().__init__(*args, **kwargs)
    
    def load_tasks(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"tasks": [], "stats": {"completed": 0, "stars": 0, "medals": 0}}
        except:
            return {"tasks": [], "stats": {"completed": 0, "stars": 0, "medals": 0}}
    
    def save_tasks(self, data):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def calculate_rewards(self, data):
        completed_tasks = len([t for t in data["tasks"] if t["completed"]])
        stars = completed_tasks
        medals = completed_tasks // 5  # 1 medalla cada 5 tareas
        
        data["stats"] = {
            "completed": completed_tasks,
            "stars": stars,
            "medals": medals
        }
        return data
    
    def do_GET(self):
        if self.path == '/':
            self.serve_main_page()
        elif self.path == '/api/tasks':
            self.serve_tasks_api()
        elif self.path.startswith('/api/'):
            self.send_error(404)
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/tasks':
            self.handle_task_creation()
        elif self.path.startswith('/api/tasks/') and self.path.endswith('/complete'):
            task_id = self.path.split('/')[-2]
            self.handle_task_completion(task_id)
        elif self.path.startswith('/api/tasks/') and self.path.endswith('/delete'):
            task_id = self.path.split('/')[-2]
            self.handle_task_deletion(task_id)
        elif self.path.startswith('/api/tasks/') and self.path.endswith('/update'):
            task_id = self.path.split('/')[-2]
            self.handle_task_update(task_id)
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sistema de Tareas - Mi Hija</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Comic Sans MS', cursive, sans-serif;
                    background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
                    min-height: 100vh;
                    padding: 20px;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    padding: 30px;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    color: #ff6b9d;
                }
                
                .header h1 {
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                }
                
                .stats {
                    display: flex;
                    justify-content: center;
                    gap: 30px;
                    margin-bottom: 30px;
                    flex-wrap: wrap;
                }
                
                .stat-card {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    min-width: 120px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }
                
                .stat-card h3 {
                    font-size: 2rem;
                    margin-bottom: 5px;
                }
                
                .stat-card p {
                    font-size: 0.9rem;
                    opacity: 0.9;
                }
                
                .form-section {
                    background: #f8f9ff;
                    padding: 25px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                }
                
                .form-section h2 {
                    color: #5a67d8;
                    margin-bottom: 20px;
                    font-size: 1.5rem;
                }
                
                .form-group {
                    margin-bottom: 15px;
                }
                
                .form-group label {
                    display: block;
                    margin-bottom: 5px;
                    color: #4a5568;
                    font-weight: bold;
                }
                
                .form-group input, .form-group textarea, .form-group select {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e2e8f0;
                    border-radius: 10px;
                    font-size: 16px;
                    transition: border-color 0.3s;
                }
                
                .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
                    outline: none;
                    border-color: #667eea;
                }
                
                .btn {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 25px;
                    border: none;
                    border-radius: 10px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: transform 0.2s;
                }
                
                .btn:hover {
                    transform: translateY(-2px);
                }
                
                .tabs {
                    display: flex;
                    background: white;
                    border-radius: 15px;
                    margin-bottom: 20px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    overflow: hidden;
                }
                
                .tab {
                    flex: 1;
                    padding: 15px 20px;
                    text-align: center;
                    background: #f8f9ff;
                    cursor: pointer;
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                    color: #5a67d8;
                    transition: all 0.3s;
                }
                
                .tab.active {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                
                .tab:hover:not(.active) {
                    background: #e2e8f0;
                }
                
                .tab-content {
                    display: none;
                }
                
                .tab-content.active {
                    display: block;
                }
                
                .calendar-grid {
                    display: grid;
                    grid-template-columns: repeat(7, 1fr);
                    gap: 10px;
                    margin-top: 20px;
                }
                
                .calendar-header {
                    background: #667eea;
                    color: white;
                    padding: 10px;
                    text-align: center;
                    border-radius: 8px;
                    font-weight: bold;
                }
                
                .calendar-day {
                    background: white;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    min-height: 100px;
                    padding: 8px;
                    position: relative;
                    cursor: pointer;
                    transition: all 0.3s;
                }
                
                .calendar-day:hover {
                    border-color: #667eea;
                    transform: translateY(-2px);
                }
                
                .calendar-day.other-month {
                    background: #f8f9fa;
                    color: #adb5bd;
                }
                
                .calendar-day.today {
                    border-color: #48bb78;
                    background: #f0fff4;
                }
                
                .day-number {
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                
                .task-dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    margin: 1px;
                    display: inline-block;
                }
                
                .task-dot.completed {
                    background: #48bb78;
                }
                
                .task-dot.pending {
                    background: #ed8936;
                }
                
                .task-dot.high-priority {
                    background: #f56565;
                }
                
                .task-modal {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    z-index: 1000;
                }
                
                .task-modal.active {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .task-modal-content {
                    background: white;
                    border-radius: 15px;
                    padding: 30px;
                    max-width: 500px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                }
                
                .task-modal h3 {
                    color: #2d3748;
                    margin-bottom: 15px;
                    font-size: 1.3rem;
                }
                
                .comments-section {
                    margin: 20px 0;
                }
                
                .comment {
                    background: #f8f9ff;
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 10px;
                    border-left: 4px solid #667eea;
                }
                
                .comment-time {
                    font-size: 0.8rem;
                    color: #718096;
                }
                
                .tasks-section {
                    margin-top: 30px;
                }
                
                .task-item {
                    background: white;
                    border: 2px solid #e2e8f0;
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    transition: all 0.3s;
                }
                
                .task-item.completed {
                    background: #f0fff4;
                    border-color: #68d391;
                }
                
                .task-info {
                    flex: 1;
                }
                
                .task-title {
                    font-size: 1.2rem;
                    font-weight: bold;
                    color: #2d3748;
                    margin-bottom: 5px;
                }
                
                .task-date {
                    color: #718096;
                    font-size: 0.9rem;
                }
                
                .task-actions {
                    display: flex;
                    gap: 10px;
                }
                
                .btn-small {
                    padding: 8px 15px;
                    font-size: 14px;
                }
                
                .btn-success {
                    background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                }
                
                .btn-danger {
                    background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
                }
                
                .calendar-section {
                    margin-top: 30px;
                    background: #f8f9ff;
                    padding: 25px;
                    border-radius: 15px;
                }
                
                .star {
                    color: #ffd700;
                    font-size: 1.5rem;
                }
                
                .medal {
                    color: #cd7f32;
                    font-size: 1.5rem;
                }
                
                @media (max-width: 768px) {
                    .stats {
                        flex-direction: column;
                        align-items: center;
                    }
                    
                    .task-item {
                        flex-direction: column;
                        gap: 15px;
                    }
                    
                    .task-actions {
                        justify-content: center;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌟 Sistema de Tareas 🌟</h1>
                    <p>¡Completa tus tareas y gana estrellas y medallas!</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <h3 id="completed-count">0</h3>
                        <p>Tareas Completadas</p>
                    </div>
                    <div class="stat-card">
                        <h3><span id="stars-count">0</span> <span class="star">⭐</span></h3>
                        <p>Estrellas Ganadas</p>
                    </div>
                    <div class="stat-card">
                        <h3><span id="medals-count">0</span> <span class="medal">🏅</span></h3>
                        <p>Medallas Ganadas</p>
                    </div>
                </div>
                
                <div class="tabs">
                    <button class="tab active" onclick="showTab('dashboard')">🏠 Panel Principal</button>
                    <button class="tab" onclick="showTab('tasks')">📋 Mis Tareas</button>
                    <button class="tab" onclick="showTab('calendar')">📅 Calendario</button>
                </div>
                
                <!-- Dashboard Tab -->
                <div id="dashboard-tab" class="tab-content active">
                    <div class="form-section">
                        <h2>📝 Agregar Nueva Tarea</h2>
                        <form id="taskForm">
                            <div class="form-group">
                                <label for="taskTitle">Título de la Tarea:</label>
                                <input type="text" id="taskTitle" name="title" required placeholder="Ej: Hacer la tarea de matemáticas">
                            </div>
                            <div class="form-group">
                                <label for="taskDescription">Descripción:</label>
                                <textarea id="taskDescription" name="description" rows="3" placeholder="Describe los detalles de la tarea..."></textarea>
                            </div>
                            <div class="form-group">
                                <label for="taskDate">Fecha Límite:</label>
                                <input type="date" id="taskDate" name="date" required>
                            </div>
                            <div class="form-group">
                                <label for="taskPriority">Prioridad:</label>
                                <select id="taskPriority" name="priority">
                                    <option value="baja">Baja</option>
                                    <option value="media" selected>Media</option>
                                    <option value="alta">Alta</option>
                                </select>
                            </div>
                            <button type="submit" class="btn">➕ Agregar Tarea</button>
                        </form>
                    </div>
                    
                    <div class="form-section">
                        <h2>📊 Resumen Rápido</h2>
                        <div id="quickSummary">
                            <!-- Resumen rápido se cargará aquí -->
                        </div>
                    </div>
                </div>
                
                <!-- Tasks Tab -->
                <div id="tasks-tab" class="tab-content">
                    <div class="tasks-section">
                        <h2>📋 Todas Mis Tareas</h2>
                        <div style="margin-bottom: 20px;">
                            <button class="btn btn-small" onclick="filterTasks('all')" id="filter-all">Todas</button>
                            <button class="btn btn-small" onclick="filterTasks('pending')" id="filter-pending">Pendientes</button>
                            <button class="btn btn-small" onclick="filterTasks('completed')" id="filter-completed">Completadas</button>
                        </div>
                        <div id="tasksList">
                            <!-- Las tareas se cargarán aquí dinámicamente -->
                        </div>
                    </div>
                </div>
                
                <!-- Calendar Tab -->
                <div id="calendar-tab" class="tab-content">
                    <div class="calendar-section">
                        <h2>📅 Calendario de Tareas</h2>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <button class="btn btn-small" onclick="changeMonth(-1)">◀ Anterior</button>
                            <h3 id="currentMonth"></h3>
                            <button class="btn btn-small" onclick="changeMonth(1)">Siguiente ▶</button>
                        </div>
                        <div class="calendar-grid" id="calendarGrid">
                            <!-- El calendario se generará aquí -->
                        </div>
                    </div>
                </div>
                
                <!-- Task Modal -->
                <div id="taskModal" class="task-modal">
                    <div class="task-modal-content">
                        <h3 id="modalTaskTitle"></h3>
                        <div id="modalTaskDetails"></div>
                        
                        <div class="comments-section">
                            <h4>💬 Comentarios y Progreso</h4>
                            <div id="commentsList"></div>
                            <div class="form-group">
                                <textarea id="newComment" placeholder="Agregar comentario sobre el progreso..." rows="3"></textarea>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="taskRequirements">🎯 ¿Qué necesitas para completar esta tarea?</label>
                            <textarea id="taskRequirements" placeholder="Ej: Necesito ayuda con las matemáticas, materiales, más tiempo..." rows="2"></textarea>
                        </div>
                        
                        <div style="display: flex; gap: 10px; margin-top: 20px;">
                            <button class="btn btn-success" onclick="updateTask(true)">✅ Marcar Completada</button>
                            <button class="btn" onclick="updateTask(false)">💾 Guardar Cambios</button>
                            <button class="btn btn-danger" onclick="closeModal()">✖ Cerrar</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                let tasks = [];
                let stats = { completed: 0, stars: 0, medals: 0 };
                let currentDate = new Date();
                let selectedTask = null;
                let currentFilter = 'all';
                
                // Cargar tareas al iniciar
                loadTasks();
                
                // Manejar envío del formulario
                document.getElementById('taskForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    addTask();
                });
                
                // Funciones de navegación por pestañas
                function showTab(tabName) {
                    // Ocultar todas las pestañas
                    document.querySelectorAll('.tab-content').forEach(tab => {
                        tab.classList.remove('active');
                    });
                    document.querySelectorAll('.tab').forEach(tab => {
                        tab.classList.remove('active');
                    });
                    
                    // Mostrar la pestaña seleccionada
                    document.getElementById(tabName + '-tab').classList.add('active');
                    event.target.classList.add('active');
                    
                    // Recargar contenido específico de la pestaña
                    if (tabName === 'calendar') {
                        setTimeout(() => updateCalendar(), 100);
                    } else if (tabName === 'tasks') {
                        updateTasksList();
                    } else if (tabName === 'dashboard') {
                        updateQuickSummary();
                    }
                }
                
                // Funciones del calendario
                function changeMonth(direction) {
                    currentDate.setMonth(currentDate.getMonth() + direction);
                    updateCalendar();
                }
                
                function updateCalendar() {
                    const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
                    
                    document.getElementById('currentMonth').textContent = 
                        monthNames[currentDate.getMonth()] + ' ' + currentDate.getFullYear();
                    
                    const calendarGrid = document.getElementById('calendarGrid');
                    calendarGrid.innerHTML = '';
                    
                    // Headers de días de la semana
                    const dayHeaders = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
                    dayHeaders.forEach(day => {
                        const header = document.createElement('div');
                        header.className = 'calendar-header';
                        header.textContent = day;
                        calendarGrid.appendChild(header);
                    });
                    
                    // Obtener primer día del mes y días en el mes
                    const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
                    const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
                    const startDate = new Date(firstDay);
                    startDate.setDate(startDate.getDate() - firstDay.getDay());
                    
                    // Generar días del calendario
                    for (let i = 0; i < 42; i++) {
                        const date = new Date(startDate);
                        date.setDate(startDate.getDate() + i);
                        
                        const dayElement = document.createElement('div');
                        dayElement.className = 'calendar-day';
                        
                        if (date.getMonth() !== currentDate.getMonth()) {
                            dayElement.classList.add('other-month');
                        }
                        
                        if (date.toDateString() === new Date().toDateString()) {
                            dayElement.classList.add('today');
                        }
                        
                        const dayNumber = document.createElement('div');
                        dayNumber.className = 'day-number';
                        dayNumber.textContent = date.getDate();
                        dayElement.appendChild(dayNumber);
                        
                        // Buscar tareas para este día
                        const dateStr = date.toISOString().split('T')[0];
                        const dayTasks = tasks.filter(task => task.date === dateStr);
                        
                        dayTasks.forEach(task => {
                            const taskDot = document.createElement('div');
                            taskDot.className = 'task-dot';
                            if (task.completed) {
                                taskDot.classList.add('completed');
                            } else if (task.priority === 'alta') {
                                taskDot.classList.add('high-priority');
                            } else {
                                taskDot.classList.add('pending');
                            }
                            taskDot.title = task.title;
                            taskDot.onclick = (e) => {
                                e.stopPropagation();
                                openTaskModal(task);
                            };
                            dayElement.appendChild(taskDot);
                        });
                        
                        calendarGrid.appendChild(dayElement);
                    }
                }
                
                // Funciones del modal de tareas
                function openTaskModal(task) {
                    selectedTask = task;
                    document.getElementById('modalTaskTitle').textContent = task.title;
                    
                    const details = document.getElementById('modalTaskDetails');
                    details.innerHTML = `
                        <p><strong>📅 Fecha:</strong> ${formatDate(task.date)}</p>
                        <p><strong>🔥 Prioridad:</strong> ${task.priority.toUpperCase()}</p>
                        <p><strong>📝 Descripción:</strong> ${task.description || 'Sin descripción'}</p>
                        <p><strong>✅ Estado:</strong> ${task.completed ? 'Completada' : 'Pendiente'}</p>
                    `;
                    
                    // Mostrar comentarios
                    const commentsList = document.getElementById('commentsList');
                    commentsList.innerHTML = '';
                    
                    if (task.comments && task.comments.length > 0) {
                        task.comments.forEach(comment => {
                            const commentDiv = document.createElement('div');
                            commentDiv.className = 'comment';
                            commentDiv.innerHTML = `
                                <div>${comment.text}</div>
                                <div class="comment-time">${formatDateTime(comment.timestamp)}</div>
                            `;
                            commentsList.appendChild(commentDiv);
                        });
                    } else {
                        commentsList.innerHTML = '<p style="color: #718096;">No hay comentarios aún</p>';
                    }
                    
                    // Llenar requisitos si existen
                    document.getElementById('taskRequirements').value = task.requirements || '';
                    document.getElementById('newComment').value = '';
                    
                    document.getElementById('taskModal').classList.add('active');
                }
                
                function closeModal() {
                    document.getElementById('taskModal').classList.remove('active');
                    selectedTask = null;
                }
                
                async function updateTask(markCompleted = false) {
                    if (!selectedTask) return;
                    
                    const comment = document.getElementById('newComment').value.trim();
                    const requirements = document.getElementById('taskRequirements').value.trim();
                    
                    const updateData = {
                        comment: comment,
                        requirements: requirements
                    };
                    
                    if (markCompleted) {
                        updateData.completed = true;
                    }
                    
                    try {
                        const response = await fetch(`/api/tasks/${selectedTask.id}/update`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(updateData)
                        });
                        
                        if (response.ok) {
                            closeModal();
                            loadTasks();
                            if (markCompleted) {
                                showMessage('¡Tarea completada! ¡Ganaste una estrella! ⭐');
                            } else {
                                showMessage('Cambios guardados correctamente 💾');
                            }
                        }
                    } catch (error) {
                        console.error('Error updating task:', error);
                    }
                }
                
                // Funciones de filtrado
                function filterTasks(filter) {
                    currentFilter = filter;
                    
                    // Actualizar botones de filtro
                    document.querySelectorAll('[id^="filter-"]').forEach(btn => {
                        btn.classList.remove('btn-success');
                    });
                    document.getElementById('filter-' + filter).classList.add('btn-success');
                    
                    updateTasksList();
                }
                
                function updateQuickSummary() {
                    const today = new Date().toISOString().split('T')[0];
                    const todayTasks = tasks.filter(task => task.date === today);
                    const pendingToday = todayTasks.filter(task => !task.completed).length;
                    const completedToday = todayTasks.filter(task => task.completed).length;
                    
                    const overdue = tasks.filter(task => !task.completed && task.date < today).length;
                    
                    document.getElementById('quickSummary').innerHTML = `
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                            <div style="background: #e6fffa; padding: 15px; border-radius: 10px; text-align: center;">
                                <h3 style="color: #319795; margin: 0;">${completedToday}</h3>
                                <p style="margin: 5px 0 0 0;">Completadas Hoy</p>
                            </div>
                            <div style="background: #fef5e7; padding: 15px; border-radius: 10px; text-align: center;">
                                <h3 style="color: #d69e2e; margin: 0;">${pendingToday}</h3>
                                <p style="margin: 5px 0 0 0;">Pendientes Hoy</p>
                            </div>
                            <div style="background: ${overdue > 0 ? '#fed7d7' : '#f0fff4'}; padding: 15px; border-radius: 10px; text-align: center;">
                                <h3 style="color: ${overdue > 0 ? '#e53e3e' : '#38a169'}; margin: 0;">${overdue}</h3>
                                <p style="margin: 5px 0 0 0;">Atrasadas</p>
                            </div>
                        </div>
                    `;
                }
                
                function formatDateTime(dateString) {
                    const options = { 
                        year: 'numeric', 
                        month: 'short', 
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    };
                    return new Date(dateString).toLocaleDateString('es-ES', options);
                }
                
                async function loadTasks() {
                    try {
                        const response = await fetch('/api/tasks');
                        const data = await response.json();
                        tasks = data.tasks || [];
                        stats = data.stats || { completed: 0, stars: 0, medals: 0 };
                        updateDisplay();
                    } catch (error) {
                        console.error('Error loading tasks:', error);
                    }
                }
                
                async function addTask() {
                    const formData = new FormData(document.getElementById('taskForm'));
                    const task = {
                        title: formData.get('title'),
                        description: formData.get('description'),
                        date: formData.get('date'),
                        priority: formData.get('priority')
                    };
                    
                    try {
                        const response = await fetch('/api/tasks', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(task)
                        });
                        
                        if (response.ok) {
                            document.getElementById('taskForm').reset();
                            loadTasks();
                            showMessage('¡Tarea agregada exitosamente! 🎉');
                        }
                    } catch (error) {
                        console.error('Error adding task:', error);
                    }
                }
                
                async function completeTask(taskId) {
                    try {
                        const response = await fetch(`/api/tasks/${taskId}/complete`, {
                            method: 'POST'
                        });
                        
                        if (response.ok) {
                            loadTasks();
                            showMessage('¡Tarea completada! ¡Ganaste una estrella! ⭐');
                        }
                    } catch (error) {
                        console.error('Error completing task:', error);
                    }
                }
                
                async function deleteTask(taskId) {
                    if (confirm('¿Estás segura de que quieres eliminar esta tarea?')) {
                        try {
                            const response = await fetch(`/api/tasks/${taskId}/delete`, {
                                method: 'POST'
                            });
                            
                            if (response.ok) {
                                loadTasks();
                                showMessage('Tarea eliminada correctamente');
                            }
                        } catch (error) {
                            console.error('Error deleting task:', error);
                        }
                    }
                }
                
                function updateDisplay() {
                    updateStats();
                    updateTasksList();
                    updateQuickSummary();
                    
                    // Solo actualizar calendario si está visible
                    const calendarTab = document.getElementById('calendar-tab');
                    if (calendarTab && calendarTab.classList.contains('active')) {
                        updateCalendar();
                    }
                }
                
                function updateStats() {
                    document.getElementById('completed-count').textContent = stats.completed;
                    document.getElementById('stars-count').textContent = stats.stars;
                    document.getElementById('medals-count').textContent = stats.medals;
                }
                
                function updateTasksList() {
                    const tasksList = document.getElementById('tasksList');
                    tasksList.innerHTML = '';
                    
                    // Filtrar tareas según el filtro actual
                    let filteredTasks = tasks;
                    if (currentFilter === 'pending') {
                        filteredTasks = tasks.filter(task => !task.completed);
                    } else if (currentFilter === 'completed') {
                        filteredTasks = tasks.filter(task => task.completed);
                    }
                    
                    if (filteredTasks.length === 0) {
                        const message = currentFilter === 'all' ? 
                            'No hay tareas aún. ¡Agrega tu primera tarea!' :
                            `No hay tareas ${currentFilter === 'pending' ? 'pendientes' : 'completadas'}`;
                        tasksList.innerHTML = `<p style="text-align: center; color: #718096;">${message}</p>`;
                        return;
                    }
                    
                    filteredTasks.forEach(task => {
                        const taskElement = document.createElement('div');
                        taskElement.className = `task-item ${task.completed ? 'completed' : ''}`;
                        taskElement.style.cursor = 'pointer';
                        
                        const priorityColors = {
                            alta: '#f56565',
                            media: '#ed8936',
                            baja: '#48bb78'
                        };
                        
                        taskElement.innerHTML = `
                            <div class="task-info" onclick="openTaskModal(tasks.find(t => t.id === '${task.id}'))">
                                <div class="task-title" style="color: ${task.completed ? '#38a169' : '#2d3748'}">
                                    ${task.completed ? '✅ ' : ''}${task.title}
                                </div>
                                <div class="task-date">
                                    📅 ${formatDate(task.date)} | 
                                    <span style="color: ${priorityColors[task.priority]}">
                                        🔥 ${task.priority.toUpperCase()}
                                    </span>
                                    ${task.comments && task.comments.length > 0 ? ` | 💬 ${task.comments.length} comentarios` : ''}
                                </div>
                                ${task.description ? `<div style="margin-top: 5px; color: #718096;">${task.description}</div>` : ''}
                                ${task.requirements ? `<div style="margin-top: 5px; color: #d69e2e; font-size: 0.9rem;">🎯 ${task.requirements}</div>` : ''}
                            </div>
                            <div class="task-actions">
                                <button class="btn btn-small" onclick="event.stopPropagation(); openTaskModal(tasks.find(t => t.id === '${task.id}'))">👁️ Ver</button>
                                ${!task.completed ? `<button class="btn btn-small btn-success" onclick="event.stopPropagation(); completeTask('${task.id}')">✅ Completar</button>` : ''}
                                <button class="btn btn-small btn-danger" onclick="event.stopPropagation(); deleteTask('${task.id}')">🗑️ Eliminar</button>
                            </div>
                        `;
                        
                        tasksList.appendChild(taskElement);
                    });
                }
                
                function updateCalendarOld() {
                    const calendar = document.getElementById('calendar');
                    const tasksByDate = {};
                    
                    tasks.forEach(task => {
                        if (!tasksByDate[task.date]) {
                            tasksByDate[task.date] = [];
                        }
                        tasksByDate[task.date].push(task);
                    });
                    
                    let calendarHTML = '';
                    for (const [date, dateTasks] of Object.entries(tasksByDate)) {
                        const completedCount = dateTasks.filter(t => t.completed).length;
                        const totalCount = dateTasks.length;
                        
                        calendarHTML += `
                            <div style="background: white; padding: 15px; margin: 10px 0; border-radius: 10px; border-left: 5px solid ${completedCount === totalCount ? '#48bb78' : '#ed8936'};">
                                <strong>📅 ${formatDate(date)}</strong> 
                                <span style="color: #718096;">(${completedCount}/${totalCount} completadas)</span>
                                <div style="margin-top: 5px;">
                                    ${dateTasks.map(task => `
                                        <span style="display: inline-block; margin: 2px 5px 2px 0; padding: 3px 8px; background: ${task.completed ? '#c6f6d5' : '#fed7d7'}; border-radius: 5px; font-size: 0.8rem;">
                                            ${task.completed ? '✅' : '⏳'} ${task.title}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                        `;
                    }
                    
                    calendar.innerHTML = calendarHTML || '<p style="text-align: center; color: #718096;">No hay tareas programadas aún</p>';
                }
                
                function formatDate(dateString) {
                    const options = { year: 'numeric', month: 'long', day: 'numeric' };
                    return new Date(dateString + 'T00:00:00').toLocaleDateString('es-ES', options);
                }
                
                function showMessage(message) {
                    const messageDiv = document.createElement('div');
                    messageDiv.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #48bb78;
                        color: white;
                        padding: 15px 20px;
                        border-radius: 10px;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                        z-index: 1000;
                        animation: slideIn 0.3s ease;
                    `;
                    messageDiv.textContent = message;
                    
                    document.body.appendChild(messageDiv);
                    
                    setTimeout(() => {
                        messageDiv.remove();
                    }, 3000);
                }
                
                // Establecer fecha de hoy como mínimo
                document.getElementById('taskDate').min = new Date().toISOString().split('T')[0];
            </script>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode('utf-8'))
    
    def serve_tasks_api(self):
        data = self.load_tasks()
        data = self.calculate_rewards(data)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def handle_task_creation(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        task_data = json.loads(post_data.decode('utf-8'))
        
        data = self.load_tasks()
        
        new_task = {
            'id': str(len(data['tasks']) + 1),
            'title': task_data['title'],
            'description': task_data.get('description', ''),
            'date': task_data['date'],
            'priority': task_data.get('priority', 'media'),
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        
        data['tasks'].append(new_task)
        data = self.calculate_rewards(data)
        self.save_tasks(data)
        
        self.send_response(201)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
    
    def handle_task_completion(self, task_id):
        data = self.load_tasks()
        
        for task in data['tasks']:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                break
        
        data = self.calculate_rewards(data)
        self.save_tasks(data)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
    
    def handle_task_update(self, task_id):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update_data = json.loads(post_data.decode('utf-8'))
        
        data = self.load_tasks()
        
        for task in data['tasks']:
            if task['id'] == task_id:
                if 'comments' not in task:
                    task['comments'] = []
                
                if 'comment' in update_data and update_data['comment'].strip():
                    task['comments'].append({
                        'text': update_data['comment'],
                        'timestamp': datetime.now().isoformat()
                    })
                
                if 'completed' in update_data:
                    task['completed'] = update_data['completed']
                    if update_data['completed']:
                        task['completed_at'] = datetime.now().isoformat()
                
                if 'requirements' in update_data:
                    task['requirements'] = update_data['requirements']
                
                break
        
        data = self.calculate_rewards(data)
        self.save_tasks(data)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
    
    def handle_task_deletion(self, task_id):
        data = self.load_tasks()
        data['tasks'] = [task for task in data['tasks'] if task['id'] != task_id]
        data = self.calculate_rewards(data)
        self.save_tasks(data)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode('utf-8'))

if __name__ == '__main__':
    import os
    
    # Para desarrollo local
    if not os.environ.get('PORT'):
        os.chdir('D:\\dev\\tareasEscolares')
    
    # Obtener puerto del entorno (Render) o usar 8001 por defecto
    port = int(os.environ.get('PORT', 8001))
    host = '0.0.0.0' if os.environ.get('PORT') else 'localhost'
    
    server = HTTPServer((host, port), TaskManagerHandler)
    print(f"Sistema de Tareas iniciado en http://{host}:{port}")
    print("Presiona Ctrl+C para detener el servidor")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSistema de Tareas detenido")
        server.shutdown()