import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const userAgent = request.headers.get('user-agent') || ''
    const ip = request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || ''
    
    const deviceType = /Mobile|Android|iPhone/i.test(userAgent) ? 'mobile' : 'desktop'
    
    const { error } = await supabase
      .from('analytics')
      .insert([{
        event_type: body.event_type,
        resource_id: body.resource_id || null,
        user_agent: userAgent,
        ip_address: ip.split(',')[0].trim(),
        device_type: deviceType,
        city: body.city || null,
        region: body.region || null,
        network_type: body.network_type || null
      }])
    
    if (error) throw error
    
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Analytics error:', error)
    return NextResponse.json({ success: false }, { status: 500 })
  }
}