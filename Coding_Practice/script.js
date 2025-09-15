// Wait for the page to load completely
document.addEventListener('DOMContentLoaded', function() {
    
    // Get our buttons
    const followBtn = document.getElementById('followBtn');
    const messageBtn = document.getElementById('messageBtn');
    const card = document.querySelector('.card');
    const skillTags = document.querySelectorAll('.skill-tag');
    
    // Track if user is following
    let isFollowing = false;
    
    // Follow button functionality
    followBtn.addEventListener('click', function() {
        if (!isFollowing) {
            // Change to following state
            this.textContent = 'Following ✓';
            this.style.background = '#4ade80';
            isFollowing = true;
            
            // Add a fun animation
            card.style.animation = 'celebrate 0.5s ease';
            
            // Show a notification
            showNotification('You are now following Sarah!');
        } else {
            // Change back to follow state
            this.textContent = 'Follow';
            this.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            isFollowing = false;
            
            showNotification('You unfollowed Sarah');
        }
    });
    
    // Message button functionality
    messageBtn.addEventListener('click', function() {
        // Add ripple effect
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 100);
        
        // Show message modal
        showNotification('Message feature coming soon! 💬');
    });
    
    // Make skill tags interactive
    skillTags.forEach(tag => {
        tag.addEventListener('click', function() {
            // Toggle selected state
            if (this.style.background === 'rgb(102, 126, 234)') {
                this.style.background = '#f0f0f0';
                this.style.color = '#555';
            } else {
                this.style.background = '#667eea';
                this.style.color = 'white';
                showNotification(`You selected ${this.textContent}!`);
            }
        });
    });
    
    // Double-click the card to "like" it
    card.addEventListener('dblclick', function() {
        // Create a heart animation
        const heart = document.createElement('div');
        heart.innerHTML = '❤️';
        heart.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 100px;
            z-index: 9999;
            animation: heartBeat 1s ease;
            pointer-events: none;
        `;
        document.body.appendChild(heart);
        
        // Remove heart after animation
        setTimeout(() => {
            heart.remove();
        }, 1000);
        
        showNotification('You liked this profile! ❤️');
    });
    
});

// Function to show notifications
function showNotification(message) {
    // Remove existing notification if any
    const existingNotif = document.querySelector('.notification');
    if (existingNotif) {
        existingNotif.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        animation: slideIn 0.3s ease;
        z-index: 1000;
        font-size: 14px;
        color: #333;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes celebrate {
        0% { transform: scale(1) rotate(0deg); }
        25% { transform: scale(1.05) rotate(-2deg); }
        50% { transform: scale(1.05) rotate(2deg); }
        75% { transform: scale(1.05) rotate(-2deg); }
        100% { transform: scale(1) rotate(0deg); }
    }
    
    @keyframes heartBeat {
        0% { 
            transform: translate(-50%, -50%) scale(0);
            opacity: 1;
        }
        50% { 
            transform: translate(-50%, -50%) scale(1.2);
            opacity: 1;
        }
        100% { 
            transform: translate(-50%, -50%) scale(1.5);
            opacity: 0;
        }
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);