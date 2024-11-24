import pygame
import numpy as np
import random
import os

class EnvironmentSimulation:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Autonomous Driving Simulation')
        
        # Load and scale the map
        try:
            map_path = os.path.join('/Users/abdulkadir/ChatbotCOT/ML2 project', 'map.png')
            self.map_img = pygame.image.load(map_path)
            self.map_img = pygame.transform.scale(self.map_img, (width, height))
            print("Map loaded successfully")
        except Exception as e:
            print(f"Error loading map: {e}")
            # Create a default background if map loading fails
            self.map_img = pygame.Surface((width, height))
            self.map_img.fill((200, 200, 200))  # Gray background
        
        # Vehicle parameters
        self.car_width = 40
        self.car_height = 60
        self.car_x = width // 2
        self.car_y = height - 100
        self.car_speed = 0
        
        # Obstacles
        self.obstacles = []
        self.generate_obstacles()
        
        # Simulation parameters
        self.clock = pygame.time.Clock()
        
    def generate_obstacles(self):
        for _ in range(3):  # Reduced number of obstacles for testing
            x = random.randint(100, self.width - 100)
            y = random.randint(-300, -50)
            obstacle = pygame.Rect(x, y, 30, 30)  # Smaller obstacles
            self.obstacles.append(obstacle)
    
    def reset(self):
        self.car_x = self.width // 2
        self.car_y = self.height - 100
        self.car_speed = 0
        self.obstacles = []
        self.generate_obstacles()
        return self._get_state()
    
    def _get_state(self):
        normalized_car_x = self.car_x / self.width
        normalized_car_y = self.car_y / self.height
        
        closest_obstacle_distance = float('inf')
        closest_obstacle_x = 0
        
        for obstacle in self.obstacles:
            distance = abs(obstacle.y - self.car_y)
            if distance < closest_obstacle_distance:
                closest_obstacle_distance = distance
                closest_obstacle_x = obstacle.x / self.width
                
        if closest_obstacle_distance == float('inf'):
            closest_obstacle_distance = 1.0
            closest_obstacle_x = 0.5
        
        return [normalized_car_x, normalized_car_y, closest_obstacle_distance / self.height, closest_obstacle_x]
    
    def step(self, action):
        # Action: 0 = left, 1 = right, 2 = accelerate, 3 = brake
        if action == 0 and self.car_x > 10:
            self.car_x -= 5
        elif action == 1 and self.car_x < self.width - self.car_width - 10:
            self.car_x += 5
        elif action == 2:
            self.car_speed = min(8, self.car_speed + 1)
        elif action == 3:
            self.car_speed = max(0, self.car_speed - 1)
        
        # Move car
        self.car_y -= self.car_speed
        
        # Move obstacles
        for obstacle in self.obstacles:
            obstacle.y += 3
        
        # Remove out-of-screen obstacles and add new ones
        self.obstacles = [obs for obs in self.obstacles if obs.y < self.height]
        if len(self.obstacles) < 3:
            self.generate_obstacles()
        
        # Check collision
        car_rect = pygame.Rect(self.car_x, self.car_y, self.car_width, self.car_height)
        collision = any(car_rect.colliderect(obs) for obs in self.obstacles)
        
        # Calculate reward
        reward = 1 if not collision else -10
        done = collision or self.car_y < 0
        
        return self._get_state(), reward, done

def main():
    # Initialize Pygame
    pygame.init()
    
    # Create environment
    env = EnvironmentSimulation()
    
    # Main game loop
    running = True
    clock = pygame.time.Clock()
    
    try:
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Clear screen
            env.screen.fill((255, 255, 255))  # White background
            
            # Draw map
            env.screen.blit(env.map_img, (0, 0))
            
            # Simulate movement
            state, reward, done = env.step(random.randint(0, 3))  # Random actions for testing
            
            # Draw car
            pygame.draw.rect(env.screen, (255, 0, 0), 
                           (env.car_x, env.car_y, env.car_width, env.car_height))
            
            # Draw obstacles
            for obstacle in env.obstacles:
                pygame.draw.rect(env.screen, (0, 0, 255), obstacle)
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            clock.tick(60)
            
            if done:
                env.reset()
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
