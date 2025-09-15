/**
 * Modern Card Component Library
 * Demonstrates advanced patterns: Web Components, Reactive State, Virtual DOM concepts
 */

// Web Component Approach
class ModernCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this._state = {
            liked: false,
            likes: 0,
            expanded: false,
            loading: false
        };
        this._props = {};
    }

    static get observedAttributes() {
        return ['title', 'description', 'image', 'variant', 'interactive'];
    }

    connectedCallback() {
        this.render();
        this.attachEventListeners();
        this.initializeIntersectionObserver();
    }

    disconnectedCallback() {
        this.cleanup();
    }

    attributeChangedCallback(name, oldValue, newValue) {
        this._props[name] = newValue;
        if (oldValue !== newValue) {
            this.render();
        }
    }

    set state(newState) {
        const oldState = { ...this._state };
        this._state = { ...this._state, ...newState };
        this.onStateChange(oldState, this._state);
        this.render();
    }

    get state() {
        return this._state;
    }

    onStateChange(oldState, newState) {
        // Virtual DOM-like diffing concept
        const changes = Object.keys(newState).filter(
            key => oldState[key] !== newState[key]
        );
        
        if (changes.length > 0) {
            this.dispatchEvent(new CustomEvent('statechange', {
                detail: { changes, oldState, newState }
            }));
        }
    }

    getStyles() {
        return `
            <style>
                :host {
                    display: block;
                    --card-bg: #ffffff;
                    --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    --card-radius: 12px;
                    --primary: #6366f1;
                    --text-primary: #1f2937;
                    --text-secondary: #6b7280;
                    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                :host([variant="dark"]) {
                    --card-bg: #1f2937;
                    --text-primary: #f3f4f6;
                    --text-secondary: #9ca3af;
                }

                .card {
                    background: var(--card-bg);
                    border-radius: var(--card-radius);
                    box-shadow: var(--card-shadow);
                    overflow: hidden;
                    transition: var(--transition);
                    position: relative;
                }

                .card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15);
                }

                .card-image {
                    width: 100%;
                    height: 200px;
                    object-fit: cover;
                    transition: transform 0.5s ease;
                }

                .card:hover .card-image {
                    transform: scale(1.05);
                }

                .card-body {
                    padding: 1.5rem;
                }

                .card-title {
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: var(--text-primary);
                    margin-bottom: 0.5rem;
                }

                .card-description {
                    color: var(--text-secondary);
                    line-height: 1.6;
                    margin-bottom: 1rem;
                }

                .card-actions {
                    display: flex;
                    gap: 0.5rem;
                    margin-top: 1rem;
                }

                button {
                    padding: 0.5rem 1rem;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 0.875rem;
                    font-weight: 500;
                    transition: var(--transition);
                }

                .btn-primary {
                    background: var(--primary);
                    color: white;
                }

                .btn-primary:hover {
                    filter: brightness(0.9);
                    transform: scale(1.05);
                }

                .like-indicator {
                    position: absolute;
                    top: 1rem;
                    right: 1rem;
                    background: white;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    transition: var(--transition);
                    cursor: pointer;
                }

                .like-indicator.liked {
                    background: #ef4444;
                    animation: heartbeat 0.6s ease;
                }

                @keyframes heartbeat {
                    0%, 100% { transform: scale(1); }
                    25% { transform: scale(1.3); }
                    50% { transform: scale(1.1); }
                }

                .skeleton {
                    animation: skeleton-loading 1s linear infinite alternate;
                }

                @keyframes skeleton-loading {
                    0% { opacity: 0.7; }
                    100% { opacity: 0.3; }
                }

                .expanded-content {
                    max-height: 0;
                    overflow: hidden;
                    transition: max-height 0.3s ease;
                }

                .expanded-content.show {
                    max-height: 200px;
                    padding-top: 1rem;
                }
            </style>
        `;
    }

    getTemplate() {
        const { title, description, image, variant } = this._props;
        const { liked, likes, loading, expanded } = this._state;

        if (loading) {
            return this.getSkeletonTemplate();
        }

        return `
            ${this.getStyles()}
            <div class="card" data-variant="${variant || 'light'}">
                ${image ? `<img class="card-image" src="${image}" alt="${title}" loading="lazy">` : ''}
                ${this._props.interactive === 'true' ? `
                    <div class="like-indicator ${liked ? 'liked' : ''}" data-action="like">
                        <span>${liked ? '❤️' : '🤍'}</span>
                    </div>
                ` : ''}
                <div class="card-body">
                    <h3 class="card-title">${title || 'Card Title'}</h3>
                    <p class="card-description">${description || 'Card description goes here'}</p>
                    ${likes > 0 ? `<p class="likes-count">${likes} likes</p>` : ''}
                    <div class="expanded-content ${expanded ? 'show' : ''}">
                        <slot name="expanded-content">Additional content here...</slot>
                    </div>
                    <div class="card-actions">
                        <button class="btn-primary" data-action="primary">
                            <slot name="primary-action">Action</slot>
                        </button>
                        ${this._props.interactive === 'true' ? `
                            <button data-action="expand">
                                ${expanded ? 'Show Less' : 'Show More'}
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    getSkeletonTemplate() {
        return `
            ${this.getStyles()}
            <div class="card skeleton">
                <div style="height: 200px; background: #e5e7eb;"></div>
                <div class="card-body">
                    <div style="height: 24px; background: #e5e7eb; margin-bottom: 8px; width: 60%;"></div>
                    <div style="height: 16px; background: #e5e7eb; margin-bottom: 4px;"></div>
                    <div style="height: 16px; background: #e5e7eb; width: 80%;"></div>
                </div>
            </div>
        `;
    }

    render() {
        this.shadowRoot.innerHTML = this.getTemplate();
    }

    attachEventListeners() {
        this.shadowRoot.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (action) {
                this.handleAction(action);
            }
        });
    }

    handleAction(action) {
        switch(action) {
            case 'like':
                this.state = {
                    liked: !this.state.liked,
                    likes: this.state.likes + (this.state.liked ? -1 : 1)
                };
                this.animateLike();
                break;
            case 'expand':
                this.state = { expanded: !this.state.expanded };
                break;
            case 'primary':
                this.dispatchEvent(new CustomEvent('primary-action', {
                    detail: { card: this }
                }));
                break;
        }
    }

    animateLike() {
        if ('vibrate' in navigator) {
            navigator.vibrate(50);
        }
    }

    initializeIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.onVisible();
                    observer.unobserve(this);
                }
            });
        }, options);

        observer.observe(this);
    }

    onVisible() {
        // Lazy load images or content
        this.dispatchEvent(new CustomEvent('visible', {
            detail: { card: this }
        }));
    }

    cleanup() {
        // Remove event listeners and observers
    }
}

// Register the Web Component
customElements.define('modern-card', ModernCard);

/**
 * Card Factory Pattern - Creating cards programmatically
 */
class CardFactory {
    static createCard(type, config) {
        const strategies = {
            'basic': () => new BasicCard(config),
            'interactive': () => new InteractiveCard(config),
            'media': () => new MediaCard(config),
            'product': () => new ProductCard(config)
        };

        const strategy = strategies[type] || strategies['basic'];
        return strategy();
    }
}

class BasicCard {
    constructor(config) {
        this.config = config;
    }

    render() {
        const card = document.createElement('modern-card');
        Object.keys(this.config).forEach(key => {
            card.setAttribute(key, this.config[key]);
        });
        return card;
    }
}

class InteractiveCard extends BasicCard {
    constructor(config) {
        super({ ...config, interactive: 'true' });
    }
}

class MediaCard extends BasicCard {
    constructor(config) {
        super(config);
        this.setupMediaFeatures();
    }

    setupMediaFeatures() {
        // Add video/audio capabilities
    }
}

class ProductCard extends BasicCard {
    constructor(config) {
        super(config);
        this.price = config.price;
        this.currency = config.currency || 'USD';
    }

    render() {
        const card = super.render();
        card.innerHTML += `
            <div slot="expanded-content">
                <p>Price: ${this.currency} ${this.price}</p>
                <button>Add to Cart</button>
            </div>
        `;
        return card;
    }
}

/**
 * Reactive Card Store (State Management)
 */
class CardStore {
    constructor() {
        this.state = new Map();
        this.subscribers = new Map();
    }

    subscribe(cardId, callback) {
        if (!this.subscribers.has(cardId)) {
            this.subscribers.set(cardId, new Set());
        }
        this.subscribers.get(cardId).add(callback);

        return () => {
            this.subscribers.get(cardId).delete(callback);
        };
    }

    setState(cardId, newState) {
        const oldState = this.state.get(cardId) || {};
        this.state.set(cardId, { ...oldState, ...newState });
        this.notify(cardId);
    }

    getState(cardId) {
        return this.state.get(cardId) || {};
    }

    notify(cardId) {
        const subscribers = this.subscribers.get(cardId);
        if (subscribers) {
            subscribers.forEach(callback => {
                callback(this.state.get(cardId));
            });
        }
    }
}

/**
 * Card Grid Manager - Handles collections of cards
 */
class CardGridManager {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            columns: options.columns || 'auto-fill',
            gap: options.gap || '2rem',
            minWidth: options.minWidth || '300px',
            animation: options.animation || true
        };
        this.cards = [];
        this.init();
    }

    init() {
        this.setupGrid();
        this.setupVirtualization();
    }

    setupGrid() {
        this.container.style.display = 'grid';
        this.container.style.gridTemplateColumns = 
            `repeat(${this.options.columns}, minmax(${this.options.minWidth}, 1fr))`;
        this.container.style.gap = this.options.gap;
    }

    setupVirtualization() {
        // Implement virtual scrolling for large lists
        const visibleCards = new Set();
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    visibleCards.add(entry.target);
                    this.loadCard(entry.target);
                } else {
                    visibleCards.delete(entry.target);
                    this.unloadCard(entry.target);
                }
            });
        }, { rootMargin: '50px' });

        this.cards.forEach(card => observer.observe(card));
    }

    addCard(cardConfig) {
        const card = CardFactory.createCard(cardConfig.type, cardConfig);
        const cardElement = card.render();
        
        if (this.options.animation) {
            cardElement.style.animation = 'fadeInUp 0.5s ease';
        }
        
        this.container.appendChild(cardElement);
        this.cards.push(cardElement);
        
        return cardElement;
    }

    removeCard(cardElement) {
        const index = this.cards.indexOf(cardElement);
        if (index > -1) {
            this.cards.splice(index, 1);
            cardElement.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => cardElement.remove(), 300);
        }
    }

    loadCard(card) {
        // Load high-res images or additional content
        card.state = { loading: false };
    }

    unloadCard(card) {
        // Free up resources for cards outside viewport
    }

    sortCards(compareFn) {
        const sorted = [...this.cards].sort(compareFn);
        sorted.forEach(card => this.container.appendChild(card));
        this.cards = sorted;
    }

    filterCards(filterFn) {
        this.cards.forEach(card => {
            card.style.display = filterFn(card) ? 'block' : 'none';
        });
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ModernCard,
        CardFactory,
        CardStore,
        CardGridManager
    };
}