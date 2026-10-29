# Génère les fichiers JSON du thème « Mme Fofana – Horizon » (thème officiel Shopify Horizon 4.3.0).
# Seuls les fichiers de ce dossier sont modifiés ; tout le reste vient d'Horizon tel quel.
# Usage : python3 build.py   (écrit templates/ et sections/ à côté de ce script)
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
G, BG, INK, GOLD, GOLDT, LINE, SOFT, CARD = '#17301F', '#F6F1E6', '#1D1D1A', '#C9A15A', '#9B6F2B', '#E1D7C2', '#EEE6D4', '#FFFCF5'
TIKTOK = 'https://www.tiktok.com/@jujufofana'
CONTACT = 'https://linktr.ee/marviejustine121'


def text(html, preset='rte', align='left', color=None, width='100%', max_width='normal', **kw):
    s = {'text': html, 'type_preset': preset, 'alignment': align, 'width': width, 'max_width': max_width}
    if color:
        s['text_color'] = color
    s.update(kw)
    return {'type': 'text', 'settings': s}


def button(label, link, style='button', **kw):
    s = {'label': label, 'link': link, 'style_class': style}
    s.update(kw)
    return {'type': 'button', 'settings': s}


def group(blocks, **settings):
    return {'type': 'group', 'settings': settings, 'blocks': dict(blocks), 'block_order': [k for k, _ in blocks]}


def section(type_, blocks=(), **settings):
    out = {'type': type_, 'settings': settings}
    if blocks:
        out['blocks'] = dict(blocks)
        out['block_order'] = [k for k, v in blocks if not v.get('static')]
    return out


def template(sections):
    return {'sections': dict(sections), 'order': [k for k, _ in sections]}


def eyebrow(label, color=GOLDT, align='left'):
    return text(f'<p>{label}</p>', preset='h6', align=align, color=color)


def product_card():
    return {
        'type': '_product-card', 'static': True, 'settings': {'product_card_gap': 6},
        'blocks': {
            'gallery': {'type': '_product-card-gallery', 'settings': {'image_ratio': 'square', 'border_radius': 8}},
            'title': {'type': 'product-title', 'settings': {'type_preset': 'rte', 'font': 'var(--font-heading--family)', 'font_size': '1.125rem', 'padding-block-start': 6}},
            'price': {'type': 'price', 'settings': {'type_preset': 'paragraph', 'show_tax_info': False, 'show_installments': False}},
        },
        'block_order': ['gallery', 'title', 'price'],
    }


# ---------------------------------------------------------------- Accueil
hero = section(
    'hero',
    [
        ('eyebrow', text('<p>Mon univers, dans votre cuisine</p>', preset='h6', align='center', color=GOLD)),
        ('title', text('<h1>La Boutique de Mme Fofana</h1>', preset='h1', align='center', color=BG, max_width='narrow')),
        ('intro', text("<p>Une sélection de mes indispensables et de mes découvertes, pour retrouver chez vous les saveurs que j'aime partager.</p>",
                       preset='paragraph', align='center', color=BG, max_width='narrow', font_size='1.125rem', **{'padding-block-end': 12})),
        ('buttons', group([
            ('shop', button('Découvrir la boutique', 'shopify://collections/all', 'button-custom',
                            custom_button_background=BG, custom_button_text=G, custom_button_border=BG)),
            ('story', button('Mon histoire', 'shopify://pages/a-propos', 'button-custom',
                             custom_button_background='rgba(0,0,0,0)', custom_button_text=BG, custom_button_border=BG)),
        ], content_direction='row', vertical_on_mobile=False, horizontal_alignment='center', gap=12, width='fit-content')),
    ],
    image_1='shopify://shop_images/hero-panier.jpg', media_type_1='image',
    content_direction='column', horizontal_alignment_flex_direction_column='center', vertical_alignment_flex_direction_column='center',
    gap=16, section_width='full-width', section_height='large',
    toggle_overlay=True, overlay_style='gradient', overlay_color='#10201AB3', gradient_direction='to top',
    **{'padding-block-start': 48, 'padding-block-end': 48},
)

marquee_items = ["Pièces artisanales de Côte d'Ivoire", 'Expédié depuis Lyon sous 2 jours', 'Mondial Relay en Point Relais ou à domicile',
                 'Livraison offerte dès 110 €', 'Paiement sécurisé']
mq_blocks = []
for i, t in enumerate(marquee_items):
    mq_blocks.append((f't{i}', text(f'<p>{t}</p>', preset='custom', color=BG, width='fit-content', wrap='nowrap',
                                    font='var(--font-subheading--family)', font_size='0.875rem', case='uppercase', letter_spacing='loose')))
    mq_blocks.append((f'i{i}', {'type': 'icon', 'settings': {'icon': 'star', 'width': 12, 'icon_color': GOLD}}))
marquee = section('marquee', mq_blocks, background_color=G, gap_between_elements=28,
                  **{'padding-block-start': 14, 'padding-block-end': 14})

def heading_group(label, title, sub=None, align='center', color=None, sub_color=None):
    items = [('eyebrow', eyebrow(label, align=align)),
             ('title', text(f'<h2>{title}</h2>', preset='h2', align=align, color=color, max_width='narrow'))]
    if sub:
        items.append(('sub', text(f'<p>{sub}</p>', preset='paragraph', align=align, color=sub_color or '#5E6158', max_width='narrow')))
    return group(items, horizontal_alignment_flex_direction_column=align if align != 'left' else 'flex-start', gap=10)


PAD = {'padding-block-start': 88, 'padding-block-end': 88}

# Mot d'accueil, juste sous le bandeau défilant
statement = section(
    'section',
    [
        ('eyebrow', eyebrow('Bienvenue', align='center')),
        ('quote', text("<p>« J'ai voulu vous faire découvrir les objets que j'utilise chez moi, ceux qui m'accompagnent en cuisine "
                       "depuis mon premier voyage en Côte d'Ivoire. »</p>", preset='custom', align='center', max_width='narrow',
                       font='var(--font-accent--family)', font_size='1.5rem', line_height='normal')),
        ('sign', text('<p>Justine — Mme Fofana</p>', preset='h6', align='center', color=GOLDT)),
    ],
    horizontal_alignment_flex_direction_column='center', gap=18, section_width='page-width',
    **{'padding-block-start': 80, 'padding-block-end': 24},
)

selection = section(
    'product-list',
    [
        ('static-header', {
            'type': '_product-list-content', 'static': True,
            'settings': {'content_direction': 'column', 'horizontal_alignment_flex_direction_column': 'center', 'gap': 10},
            'blocks': {
                'eyebrow': {'type': '_product-list-text', 'settings': {'text': '<p>Ma sélection</p>', 'type_preset': 'h6', 'alignment': 'center', 'text_color': GOLDT}},
                'title': {'type': '_product-list-text', 'settings': {'text': '<h2>Les Trésors de Chez Nous</h2>', 'type_preset': 'h2', 'alignment': 'center'}},
                'sub': {'type': '_product-list-text', 'settings': {'text': '<p>Mortiers, pilons et plateaux sculptés à la main, en quantités limitées.</p>',
                                                                    'type_preset': 'paragraph', 'alignment': 'center', 'text_color': '#5E6158'}},
            },
            'block_order': ['eyebrow', 'title', 'sub'],
        }),
        ('static-product-card', product_card()),
        ('all', button('Voir toute la boutique', 'shopify://collections/all', 'button')),
    ],
    collection='all', layout_type='carousel', carousel_on_mobile=True, max_products=12, columns=4, mobile_columns='2',
    mobile_card_size='60cqw', columns_gap=20, rows_gap=32, icons_style='arrow', icons_shape='circle',
    section_width='page-width', horizontal_alignment='center', gap=40,
    **{'padding-block-start': 56, 'padding-block-end': 88},
)

def collection_card():
    return {
        'type': '_collection-card', 'static': True,
        'settings': {'placement': 'on_image', 'horizontal_alignment': 'flex-start', 'vertical_alignment': 'flex-end',
                     'collection_card_gap': 4, 'border_radius': 12},
        'blocks': {
            'collection-card-image': {'type': '_collection-card-image', 'static': True,
                                      'settings': {'image_ratio': 'portrait', 'toggle_overlay': True, 'overlay_style': 'gradient',
                                                   'overlay_color': '#10201ACC', 'gradient_direction': 'to top', 'border_radius': 12}},
            'collection-title': {'type': 'collection-title',
                                 'settings': {'type_preset': 'h3', 'text_color': BG, 'padding-inline-start': 24, 'padding-inline-end': 24}},
            'cta': text('<p>Découvrir →</p>', preset='h6', color=GOLD, **{'padding-inline-start': 24, 'padding-block-end': 24}),
        },
        'block_order': ['collection-title', 'cta'],
    }

univers = section(
    'collection-list',
    [
        ('header', heading_group('Explorer', 'Par univers', 'Des ustensiles pour cuisiner comme en Côte d’Ivoire, des plateaux pour servir avec caractère.')),
        ('static-collection-card', collection_card()),
    ],
    collection_list=['cuisine', 'service-de-table'], layout_type='grid', columns=2, mobile_columns='1', max_collections=2,
    columns_gap=20, rows_gap=20, section_width='page-width', gap=40, background_color=SOFT, **PAD,
)

apropos_text = ("<p>Française d’origine, je suis passionnée par les cultures du monde et particulièrement par les richesses de l’Afrique. "
                "Depuis mon premier voyage en Côte d’Ivoire en 2019, j’y suis retournée à plusieurs reprises et je me suis attachée "
                "à sa cuisine et à ses traditions.</p><p>Cette boutique est le prolongement naturel de cet univers : les ustensiles qui "
                "m’accompagnent en cuisine et les pièces artisanales que je prends plaisir à dénicher.</p>")

# Texte d'abord (sur mobile la photo vient après, plus de saut brutal), photo encadrée à droite sur ordinateur
about = section(
    'section',
    [
        ('content', group([
            ('eyebrow', eyebrow('À propos')),
            ('title', text('<h2>Française et ivoirienne de cœur</h2>', preset='h2', max_width='narrow')),
            ('body', text(apropos_text, preset='rte', max_width='narrow')),
            ('sign', text('<p>Justine Fofana</p>', preset='custom', font='var(--font-accent--family)', font_size='1.5rem', color=GOLDT)),
            ('buttons', group([
                ('story', button('Lire mon histoire', 'shopify://pages/a-propos', 'button')),
                ('tiktok', button('Me suivre sur TikTok', TIKTOK, 'button-secondary', open_in_new_tab=True)),
            ], content_direction='row', vertical_on_mobile=False, gap=12, width='fit-content')),
        ], gap=18, width='custom', custom_width=50, width_mobile='fill')),
        ('photo', {'type': 'image', 'settings': {'image': 'shopify://shop_images/mme-fofana.jpg', 'image_ratio': 'portrait',
                                                 'width': 'custom', 'custom_width': 42, 'width_mobile': 'fill', 'border_radius': 12}}),
    ],
    content_direction='row', vertical_on_mobile=True, horizontal_alignment='space-between', vertical_alignment='center',
    gap=48, section_width='page-width', **PAD,
)

promesses = [
    ('serving_dish', 'Artisanat authentique', "Sculptées à la main en Côte d'Ivoire, chaque pièce est unique."),
    ('heart', 'Choisi avec soin', "Uniquement des objets que j'utilise et que j'aime chez moi."),
    ('truck', 'Expédié depuis Lyon', 'Sous 2 jours, en Point Relais ou à domicile. Offert dès 110 €.'),
    ('return', '14 jours pour changer d’avis', 'Tous les produits peuvent être retournés.'),
]
cards = []
for i, (ic, h, t) in enumerate(promesses):
    cards.append((f'p{i}', group([
        ('icon', {'type': 'icon', 'settings': {'icon': ic, 'width': 28, 'icon_color': GOLDT}}),
        ('h', text(f'<h3>{h}</h3>', preset='h5')),
        ('t', text(f'<p>{t}</p>', preset='rte')),
    ], gap=10, background_color=CARD, border='solid', border_width=1, border_color=LINE, border_radius=12,
       **{'padding-block-start': 28, 'padding-block-end': 28, 'padding-inline-start': 24, 'padding-inline-end': 24})))
promises = section(
    'section',
    [
        ('header', heading_group('Nos engagements', 'Acheter chez Mme Fofana')),
        ('cards', group(cards, content_direction='row', vertical_on_mobile=True, gap=16)),
    ],
    horizontal_alignment_flex_direction_column='center', gap=40, section_width='page-width', background_color=SOFT, **PAD,
)

newsletter = section(
    'section',
    [
        ('eyebrow', eyebrow('Newsletter', color=GOLD, align='center')),
        ('title', text('<h2>Envie de découvrir les prochaines nouveautés ?</h2>', preset='h2', align='center', color=BG, max_width='narrow')),
        ('text', text('<p>Nouveaux produits, offres et actualités de la boutique, directement dans votre boîte mail.</p>',
                      preset='paragraph', align='center', color='#D9D2C3', max_width='narrow')),
        ('form', {'type': 'email-signup', 'settings': {
            'width': 'custom', 'custom_width': 60, 'border_style': 'all', 'input_style': 'custom', 'border_radius': 4,
            'input_background_color': CARD, 'input_text_color': INK, 'input_border_color': CARD,
            'style_class': 'button-custom', 'custom_button_background': GOLD, 'custom_button_text': G, 'custom_button_border': GOLD,
            'display_type': 'text', 'label': "Je m'inscris", 'integrated_button': False}}),
    ],
    horizontal_alignment_flex_direction_column='center', gap=16, background_color=G, **PAD,
)

index = template([('hero', hero), ('marquee', marquee), ('statement', statement), ('selection', selection), ('univers', univers),
                  ('about', about), ('promises', promises), ('newsletter', newsletter)])

# ---------------------------------------------------------------- Fiche produit
caracteristiques = ("{%- assign c = product.metafields.custom.caracteristiques.value -%}"
                    "{%- if c != blank -%}<ul style=\"margin:0;padding-left:1.1em;display:grid;gap:.35em\">"
                    "{%- assign lines = c | newline_to_br | split: '<br />' -%}"
                    "{%- for l in lines -%}{%- assign l = l | strip -%}{%- if l != blank -%}<li>{{ l }}</li>{%- endif -%}{%- endfor -%}</ul>{%- endif -%}")

def row(heading, icon, inner_blocks, open_=False):
    return {'type': '_accordion-row', 'settings': {'heading': heading, 'icon': icon, 'width': 20, 'open_by_default': open_},
            'blocks': dict(inner_blocks), 'block_order': [k for k, _ in inner_blocks]}

product = template([
    ('main', {
        'type': 'product-information',
        'settings': {'content_width': 'content-center-aligned', 'desktop_media_position': 'left', 'equal_columns': False,
                     'limit_details_width': True, 'gap': 48, 'padding-block-start': 24, 'padding-block-end': 48},
        'blocks': {
            'media-gallery': {'type': '_product-media-gallery', 'static': True, 'settings': {
                'media_presentation': 'carousel', 'media_columns': 'one', 'image_gap': 8, 'large_first_image': True,
                'icons_style': 'arrows_large', 'slideshow_controls_style': 'thumbnails', 'slideshow_mobile_controls_style': 'dots',
                'thumbnail_position': 'bottom', 'aspect_ratio': '1', 'media_fit': 'cover', 'media_radius': 8,
                'constrain_to_viewport': True, 'zoom': True, 'hide_variants': False}},
            'product-details': {'type': '_product-details', 'static': True,
                                'settings': {'gap': 20, 'sticky_details_desktop': True, 'details_position': 'flex-start'},
                                'blocks': {
                                    'eyebrow': {'type': 'custom-liquid', 'settings': {'custom_liquid': '<p style="margin:0;color:#9B6F2B;font-family:var(--font-subheading--family);font-size:.75rem;letter-spacing:.14em;text-transform:uppercase">{{ product.type }}</p>'}},
                                    'title': text('<h1>{{ closest.product.title }}</h1>', preset='h3'),
                                    'price': {'type': 'price', 'settings': {'type_preset': 'h4', 'show_tax_info': False, 'show_installments': False}},
                                    'tva': text('<p>TVA non applicable, art. 293 B du CGI. Frais de livraison calculés au paiement.</p>',
                                                preset='custom', font_size='0.75rem', color='#5E6158'),
                                    'divider': {'type': '_divider', 'settings': {'thickness': 1, 'divider_color': LINE, 'width_percent': 100}},
                                    'variants': {'type': 'variant-picker', 'settings': {'variant_style': 'buttons', 'show_swatches': False, 'alignment': 'left'}},
                                    'stock': {'type': 'product-inventory', 'settings': {'inventory_threshold': 5, 'show_inventory_quantity': True, 'text_color': GOLDT}},
                                    'buy': {'type': 'buy-buttons', 'settings': {'stacking': True, 'show_pickup_availability': False, 'gift_card_form': True},
                                            'blocks': {'quantity': {'type': 'quantity', 'static': True},
                                                       'add-to-cart': {'type': 'add-to-cart', 'static': True, 'settings': {'style_class': 'button'}},
                                                       'accelerated-checkout': {'type': 'accelerated-checkout', 'static': True}},
                                            'block_order': []},
                                    'reassurance': group([
                                        ('a', {'type': 'icon', 'settings': {'icon': 'truck', 'width': 18, 'icon_color': G}}),
                                        ('b', text('<p>Expédié depuis Lyon sous 2 jours · Livraison offerte dès 110 €</p>', preset='custom', font_size='0.875rem')),
                                    ], content_direction='row', vertical_on_mobile=False, gap=10, background_color=SOFT, border_radius=6,
                                        **{'padding-block-start': 12, 'padding-block-end': 12, 'padding-inline-start': 14, 'padding-inline-end': 14}),
                                    'description': text('{{ closest.product.description }}', preset='rte'),
                                    'accordion': {'type': 'accordion', 'settings': {'icon': 'plus', 'dividers': True, 'divider_color': LINE, 'type_preset': 'h6'},
                                                  'blocks': {
                                                      'carac': row('Caractéristiques', 'ruler', [('c', {'type': 'custom-liquid', 'settings': {'custom_liquid': caracteristiques}})], True),
                                                      'livraison': row('Livraison', 'truck', [('t', text(
                                                          '<p>Expédition depuis Lyon sous 2 jours ouvrés, par Mondial Relay en Point Relais ou à domicile (3 à 5 jours). '
                                                          'Frais selon le poids, affichés au paiement. <strong>Offerte dès 110 € d’achats.</strong></p>'))]),
                                                      'retours': row('Retours', 'return', [('t', text(
                                                          '<p>14 jours après réception pour changer d’avis. Tous les produits peuvent être repris. '
                                                          '<a href="/pages/livraison-et-retours">Voir les conditions</a>.</p>'))]),
                                                      'artisanat': row('Une pièce artisanale', 'heart', [('t', text(
                                                          '<p>Chaque pièce est faite à la main : de légères différences de forme, de teinte ou de veinage '
                                                          'avec les photos sont normales et font son authenticité.</p>'))]),
                                                  },
                                                  'block_order': ['carac', 'livraison', 'retours', 'artisanat']},
                                },
                                'block_order': ['eyebrow', 'title', 'price', 'tva', 'divider', 'variants', 'stock', 'buy', 'reassurance', 'description', 'accordion']},
        },
        'block_order': [],
    }),
    ('recommendations', {
        'type': 'product-recommendations',
        'settings': {'product': '{{ closest.product }}', 'recommendation_type': 'related', 'layout_type': 'carousel', 'carousel_on_mobile': True,
                     'max_products': 4, 'columns': 4, 'mobile_columns': '2', 'columns_gap': 16, 'rows_gap': 24,
                     'icons_style': 'arrow', 'icons_shape': 'circle', 'section_width': 'page-width', 'gap': 28,
                     'padding-block-start': 48, 'padding-block-end': 72},
        'blocks': {'title': text('<h2>Tu aimeras aussi</h2>', preset='h3'), 'static-product-card': product_card()},
        'block_order': ['title'],
    }),
])

# ---------------------------------------------------------------- Page À propos
page_apropos = template([
    ('about', section(
        'section',
        [
            ('content', group([
                ('eyebrow', eyebrow('À propos')),
                ('title', text('<h1>Française et ivoirienne de cœur</h1>', preset='h1', max_width='narrow')),
                ('body', text(
                    "<p>Je m’appelle Justine Fofana, connue sous le nom de Mme Fofana. Française d’origine, je suis passionnée par les cultures du monde et particulièrement par les richesses de l’Afrique.</p>"
                    "<p>J’ai découvert la Côte d’Ivoire pour la première fois en 2019, à l’âge de 16 ans. Depuis, j’y suis retournée à plusieurs reprises et j’ai développé un véritable attachement à ses cultures, à sa cuisine et à ses traditions. À travers mon mari, mes amies sénégalaises, maliennes et mes rencontres, j’ai aussi découvert de nombreuses autres spécialités africaines qui inspirent aujourd’hui ma cuisine.</p>"
                    "<p>Sur mes réseaux sociaux, je partage mes recettes, mes découvertes et des moments de mon quotidien avec une communauté qui grandit chaque jour.</p>"
                    "<p><strong>La Boutique de Mme Fofana est le prolongement naturel de cet univers.</strong> J’ai voulu vous faire découvrir les objets que j’utilise chez moi, les ustensiles qui m’accompagnent en cuisine et les pièces artisanales que je prends plaisir à dénicher, en Côte d’Ivoire et ailleurs.</p>"
                    "<p>Cette sélection évoluera au fil de mes découvertes, avec de nouveaux produits, des nouveautés et des offres à retrouver régulièrement.</p>",
                    preset='rte', max_width='narrow')),
                ('sign', text('<p>Justine Fofana</p>', preset='custom', font='var(--font-accent--family)', font_size='1.5rem', color=GOLDT)),
                ('buttons', group([
                    ('shop', button('Découvrir la boutique', 'shopify://collections/all', 'button')),
                    ('tiktok', button('Me suivre sur TikTok', TIKTOK, 'button-secondary', open_in_new_tab=True)),
                ], content_direction='row', vertical_on_mobile=False, gap=12, width='fit-content')),
            ], gap=18, width='custom', custom_width=52, width_mobile='fill')),
            ('photo', {'type': 'image', 'settings': {'image': 'shopify://shop_images/mme-fofana.jpg', 'image_ratio': 'portrait',
                                                     'width': 'custom', 'custom_width': 40, 'width_mobile': 'fill', 'border_radius': 12}}),
        ],
        content_direction='row', vertical_on_mobile=True, horizontal_alignment='space-between', vertical_alignment='flex-start',
        gap=48, section_width='page-width', **{'padding-block-start': 64, 'padding-block-end': 88},
    )),
    ('promises', promises),
    ('newsletter', newsletter),
])

# ---------------------------------------------------------------- En-tête et pied de page
header_group = {
    'type': 'header', 'name': 'En-tête',
    'sections': {
        'announcements': {
            'type': 'header-announcements',
            'settings': {'speed': 5, 'section_width': 'page-width', 'background_color': G, 'divider_width': 0,
                         'padding-block-start': 10, 'padding-block-end': 10},
            'blocks': {
                'a1': {'type': '_announcement', 'settings': {'text': 'Livraison offerte dès 110 € en France', 'link': 'shopify://pages/livraison-et-retours',
                                                              'font': 'var(--font-subheading--family)', 'font_size': '0.75rem', 'letter_spacing': 'loose', 'case': 'uppercase', 'text_color': BG}},
                'a2': {'type': '_announcement', 'settings': {'text': 'Expédié depuis Lyon sous 2 jours · Mondial Relay',
                                                              'font': 'var(--font-subheading--family)', 'font_size': '0.75rem', 'letter_spacing': 'loose', 'case': 'uppercase', 'text_color': BG}},
            },
            'block_order': ['a1', 'a2'],
        },
        'header_section': {
            'type': 'header',
            'settings': {'logo_position': 'center', 'menu_position': 'left', 'menu_row': 'top', 'show_search': True, 'search_position': 'right',
                         'search_row': 'top', 'show_country': False, 'show_language': False, 'section_width': 'page-width', 'section_height': 'standard',
                         'enable_sticky_header': 'always', 'divider_width': 1, 'divider_size': 'full-width', 'border_width': 0,
                         'enable_transparent_header_home': False, 'enable_transparent_header_product': False, 'enable_transparent_header_collection': False},
            'blocks': {
                'header-logo': {'type': '_header-logo', 'static': True, 'settings': {'hide_logo_on_home_page': False}},
                'header-menu': {'type': '_header-menu', 'static': True, 'settings': {
                    'menu': 'main-menu', 'type_font_primary_size': '0.875rem', 'menu_font_style': 'regular', 'type_font_primary_link': 'heading',
                    'type_case_primary_link': 'none', 'menu_style': 'featured_products', 'navigation_bar': False}},
            },
        },
    },
    'order': ['announcements', 'header_section'],
}

footer_group = {
    'type': 'footer', 'name': 'Pied de page',
    'sections': {
        'footer': {
            'type': 'footer',
            'settings': {'section_width': 'page-width', 'gap': 48, 'background_color': SOFT, 'padding-block-start': 56, 'padding-block-end': 40},
            'blocks': {
                'brand': group([
                    ('logo', {'type': 'image', 'settings': {'image': 'shopify://shop_images/logo-mme-fofana.png', 'width': 'custom', 'custom_width': 70, 'width_mobile': 'custom', 'custom_width_mobile': 70}}),
                    ('tag', text('<p>Ustensiles &amp; art de vivre africains, sélectionnés avec soin et expédiés depuis Lyon.</p>', preset='rte', max_width='narrow')),
                    ('social', {'type': 'social-links', 'settings': {'icon_color': G, 'instagram_url': 'https://www.instagram.com/juju_fofana',
                                                                    'tiktok_url': TIKTOK, 'snapchat_url': 'https://snapchat.com/t/VUMKoSqa',
                                                                    'facebook_url': 'https://www.facebook.com/share/1GzJyVUD8a/'}}),
                ], gap=12),
                'menu_shop': {'type': 'menu', 'settings': {'menu': 'main-menu', 'heading': 'La boutique', 'menu_spacing': 10, 'heading_preset': 'h6', 'link_preset': 'paragraph'}},
                'menu_help': {'type': 'menu', 'settings': {'menu': 'footer', 'heading': 'Infos utiles', 'menu_spacing': 10, 'heading_preset': 'h6', 'link_preset': 'paragraph'}},
                'contact': group([
                    ('h', text('<p>Une question ?</p>', preset='h6', color=GOLDT)),
                    ('t', text('<p><a href="mailto:mmefofana.boutique@gmail.com">mmefofana.boutique@gmail.com</a></p><p>Réponse sous 48 h.</p>', preset='rte')),
                    ('b', button('Écris-moi', CONTACT, 'button-secondary', open_in_new_tab=True)),
                    ('pay', {'type': 'payment-icons', 'settings': {}}),
                ], gap=10),
            },
            'block_order': ['brand', 'menu_shop', 'menu_help', 'contact'],
        },
        'utilities': {
            'type': 'footer-utilities',
            'settings': {'section_width': 'page-width', 'gap': 24, 'background_color': SOFT, 'divider_thickness': 1, 'divider_color': LINE,
                         'padding-block-start': 16, 'padding-block-end': 20},
            'blocks': {
                'copyright': {'type': 'footer-copyright', 'settings': {'show_powered_by': False, 'font_size': '0.75rem', 'case': 'none'}},
                'policy_list': {'type': 'footer-policy-list', 'settings': {'font_size': '0.75rem', 'case': 'none'}},
            },
            'block_order': ['copyright', 'policy_list'],
        },
    },
    'order': ['footer', 'utilities'],
}

files = {
    'templates/index.json': index,
    'templates/product.json': product,
    'templates/page.a-propos.json': page_apropos,
    'sections/header-group.json': header_group,
    'sections/footer-group.json': footer_group,
}
for name, data in files.items():
    path = os.path.join(ROOT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(name, os.path.getsize(path))
