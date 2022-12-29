<?php
// (c) @AbirHasan2005

function get_deals() {
    $deals = [];
    $soup = file_get_contents('https://www.amazon.com/gp/goldbox');
    $assets = preg_match_all("/assets\.mountWidget\(.*\)/", $soup, $matches);
    $json_data = json_decode(substr($matches[0][0], 29, strlen($matches[0][0])-30));
    $parsed_data = $json_data->prefetchedData->aapiGetDealsList[0]->entities;
    foreach ( $parsed_data as $raw_data) {
        $title = $raw_data->entity->details->entity->title;
        $deal_type = $raw_data->entity->details->entity->type;
        $link = 'https://www.amazon.com' . $raw_data->entity->details->entity->landingPage->url;
        $data = ['title' => $title, 'deal_type' => $deal_type, 'link' => $link];
        try {
            $price_data = $raw_data->entity->details->entity->price->details;
        } catch (Exception $e) {
            $price_data = [];
        }
        $data['price_data'] = $price_data;
        $deals[] = $data;
    }
    return $deals;
}


print_r(get_deals());
