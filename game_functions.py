import sys
from time import sleep


import pygame
import shelve
import random
from pygame import mixer
from bullet import Bullet 
from alien import Alien


def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """Respond to keypresses."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def check_keyup_events(event, ship):
    """Respond to key releases."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
    """Respond to keypresses and mouse events."""        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # with open('high_score.txt','w') as file_object:
			#     file_object.write(str(stats.high_score))
            sys.exit()
        elif  event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y)


def check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y):
    """Start a new game when the player clicks Play."""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        # Reset the game settings.
        ai_settings.initialize_dynamic_settings()


        # Hide the mouse cursor
        pygame.mouse.set_visible(False)

        # Reset the game sttatistics
        stats.reset_stats()
        stats.game_active = True

        # Reset the score board images.
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

        # Empty the list of aliens and bullets
        aliens.empty()
        bullets.empty()

        # Create a new fleet and center the ship.
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()


def fire_bullet(ai_settings, screen, ship, bullets):
    """Fire a bullet if limit not reached yet."""
    # Bullet sound
    bullet_sound = mixer.Sound("./assets/music/sfx/fire_bullet.mp3")
    bullet_sound.play()
    # Create a new bullet and add it to the bullets group.
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def redraw_window(ai_settings, screen):
    """Redraw the background images to give infinite motion"""
    # Flip the copy of the background image for infinite image illusion
    bg_flipped = pygame.transform.flip(ai_settings.bg_copy, False, True)

    # Redraw the bacground image and flipped copy side by side verticaly
    screen.blit(ai_settings.background, (0, ai_settings.bgY))
    screen.blit(bg_flipped, (0, ai_settings.bgY2))

def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    """Update images on the screen and flip to the new screen."""
    # Redraw the screen during each pass through the loop
    redraw_window(ai_settings, screen)

    ai_settings.clock.tick(ai_settings.pace)
    # Move images downwards a little
    ai_settings.bgY += ai_settings.bg_speed
    ai_settings.bgY2 += ai_settings.bg_speed

    # Send bg image to the back when the pass the screen (like an image loop)
    if ai_settings.bgY > ai_settings.background.get_height():
        ai_settings.bgY = ai_settings.background.get_height() * -1
    if ai_settings.bgY2 > ai_settings.background.get_height():
        ai_settings.bgY2 = ai_settings.background.get_height() * -1



    # screen.fill(ai_settings.bg_color)
    # screen.blit(ai_settings.background, (0,0,0,0))

    # Redraw all the bullets bullets behind ship and aliens.
    ship.blitme()
    aliens.draw(screen)
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    # Draw the score information.
    sb.show_score()

    # Draw the play button if the game is active
    if not stats.game_active:
        
        play_button.draw_button()

    # Make the most recently drawn sreen visible.
    pygame.display.flip()


def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Update position of bullets and get rid of old bullets."""
    # Update bullet positions.
    bullets.update()

    # Get rid of bullets that have disappeared.
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets)


def check_high_score(stats, sb):
    """Check to see if there's a new high score."""
    if stats.score > stats.high_score:
        d = shelve.open('high_score')
        d['high_score'] = stats.score
        stats.high_score = d['high_score']
        sb.prep_high_score()
        d.close()


def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Respond to bullet-alien collisions."""

    # Remove any bullets and aliens that have collided.
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        # Hit Alien Sound
        bullet_sound = mixer.Sound("./assets/music/sfx/bullet_hit_alien.wav")
        bullet_sound.play()

        # loop through a list of aliens hit by one bullet
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)

    if len(aliens) == 0:
        # If the entire fleet is destroyed, start new level.
        bullets.empty()
        ai_settings.increase_speed()

        # Increase level.
        stats.level += 1
        sb.prep_level()

        create_fleet(ai_settings, screen, ship, aliens)

def check_fleet_edges(ai_settings, aliens):
    """Respond appropriatley if any aliens have reached an edge."""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """Drop the entire fllet and change the fleet's direction."""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    """Respond to ship being hit by alien."""
    if stats.ships_left > 0:
        # Decrement ships_left.
        stats.ships_left -= 1

        # Update scoreboard
        sb.prep_ships()
    else:
        stats.game_active = False
        play_button.prep_msg("New Game")
        pygame.mouse.set_visible(True)

    # Empty the list of aliens and bullets
    aliens.empty()
    bullets.empty()

    # Create a new fleetand center the ship.
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()

    # Pause
    sleep(0.5)


def check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    """Check if any aliens have reached the bottom of the screen."""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Treat this the same as if the ship got hit.
            ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button)
            break


def update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    """
    Check if the fleet is at an edge,
      and then update the positions of all aliens in the fleet. 
    """
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # Look for alien-ship collisions.
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button)
    
    # Look for aliens hitting the bottom of the screen.
    check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button)


def get_number_aliens_x(ai_settings, alien_width):
    """Determine the number of aliens that fit in a row."""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    """Determine the number of rows of aliens that fit on the screen."""
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows

def create_alien(ai_settings, screen, aliens, alien_number, row_number, rdm_img_path):
    """Create an alien and place it in a row."""

    alien = Alien(ai_settings, screen, rdm_img_path)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """Create a full fleet of aliens."""

    # New fleet sound
    bullet_sound = mixer.Sound("./assets/music/sfx/create_fleet.wav")
    bullet_sound.play()
    # Create an alien and find the number of aliens in a row.

    # Get random alien image
    img_list = ["./assets/img/ufo1.png", "./assets/img/ufo2.png", "./assets/img/ufo3.png", "./assets/img/ufo4.png",]
    rdm_img_index = random.randint(0, (len(img_list) - 1))
    rdm_img_path = img_list[rdm_img_index]

    alien = Alien(ai_settings, screen, rdm_img_path)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)
    
    # Create the fleet of aliens.
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number, rdm_img_path)













    

