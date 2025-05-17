// Test file for debugging property assignment issues
document.addEventListener("DOMContentLoaded", function() {
    let testData = [
        {
            "modelo": "Test Moto 1",
            "marca": "Test Brand 1",
            "precio": 10000,
            "estilo": "Sport",
            "imagen": "test1.jpg",
            "score": 0.85,
            "razones": ["Razón 1", "Razón 2"]
        },
        {
            "modelo": "Test Moto 2",
            "marca": "Test Brand 2",
            "precio": 15000,
            "estilo": "Adventure",
            "imagen": "test2.jpg",
            "score": 0.75,
            "razones": ["Razón 3", "Razón 4"]
        }
    ];
    
    // Assign to window object
    window.testRecomendaciones = testData;
    
    console.log("Test data assigned:", window.testRecomendaciones);
});
